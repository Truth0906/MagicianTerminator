import traceback
import sys
import time
import os.path
sys.path.append('../PTTCrawlerLibrary')
import PTT
import MagicianTerminatorCondition
import json
from time import gmtime, strftime
print('Magician Terminator')

Board = 'Wanted'
Retry = True
# If you want to automatically login define Account.txt
# {'ID':'YourID', 'Password':'YourPW'}

Test = False

try:
    with open('Account.txt', encoding = 'utf-8-sig') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
    print('Auto ID password mode')
except FileNotFoundError:
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

def Log(InputMessage, ends='\r\n'):
    TotalMessage = '[' + strftime('%Y-%m-%d %H:%M:%S') + '] ' + InputMessage
    print(TotalMessage.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), end=ends)

PTTCrawler = PTT.Crawler(ID, Password, False)
if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    
    MailList = []

    try:
        with open('MailList.txt') as MailListFile:
            MailList = MailListFile.readlines()
        MailList = [x.strip() for x in MailList] 
    except FileNotFoundError:
        file = open('MailList.txt', 'w')
        file.close()
    
    PTTCrawler.Log('載入記錄名單完成')
    
    Content = PTTCrawler.readPostFile('Mail.txt')
    
    if Content == None:
        PTTCrawler.Log('載入信件檔案失敗')
        PTTCrawler.logout()
        sys.exit()
    PTTCrawler.Log('載入信件檔案完成')
    
    PTTCrawler.Log('內文: ' + Content)
    
    if os.path.exists('LastPostIndex.txt'):
        
        LastIndex = 0
        f = open('LastPostIndex.txt', 'r')
        LastIndex = int(f.readline())
        if LastIndex <= 0:
            LastIndexList = [0]
        else:
            LastIndexList = [LastIndex - 1]
        f.close()
        
        if not Test:
            PTTCrawler.Log('重新檢查文章編號 ' + str(LastIndexList[0]))
        
    else :
        LastIndex = 0
        LastIndexList = [0]
    
    First = True
    
    while Retry:
    
        try:
            if not len(LastIndexList) == 0:
                ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
                
                LastIndex = LastIndexList.pop()
            
            if First:
                First = False
                
                if len(LastIndexList) == 0 and LastIndex == 0:
                
                    RecheckPost = 60
                    LastIndex = NewestIndex - RecheckPost
                    PTTCrawler.Log('重新檢查過去 ' + str(RecheckPost) + ' 篇文章')
                elif Test:
                    RecheckPost = 1000
                    LastIndex = NewestIndex - RecheckPost
                    PTTCrawler.Log('測試過去 ' + str(RecheckPost) + ' 篇文章')
                    
            ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList(Board, LastIndex)
            if ErrorCode != PTTCrawler.Success:
                PTTCrawler.Log('Get newest list error: ' + str(ErrorCode))
                time.sleep(1)
                continue
            
            if not len(LastIndexList) == 0:
                #PTTCrawler.Log('偵測到 ' + str(len(LastIndexList)) + ' 篇新文章')
                for NewPostIndex in LastIndexList:
                    #PTTCrawler.Log('檢查文章編號 ' + str(NewPostIndex))
                    
                    ErrorCode, NewPost = PTTCrawler.getPostInfoByIndex(Board, NewPostIndex)
                    if ErrorCode == PTTCrawler.PostDeleted:
                        #PTTCrawler.Log('文章編號 ' + str(NewPostIndex) + ' 已經被刪除')
                        continue
                    if ErrorCode != PTTCrawler.Success:
                        #PTTCrawler.Log('文章編號 ' + str(NewPostIndex) + ' 取得錯誤')
                        continue
                    if NewPost == None:
                        PTTCrawler.Log('Post is empty')
                        continue
                        
                    if not NewPost == None:
                        #Special condition
                        if MagicianTerminatorCondition.needStore(NewPost):
                        
                            PostAuthor = NewPost.getPostAuthor()
                            PostAuthor = PostAuthor[:PostAuthor.find(' (')]
                            
                            PTTCrawler.Log('賓果! ' + Board + ' ' + str(NewPostIndex) + ' ' + PostAuthor)
                            
                            if not PostAuthor in MailList:
                            
                                #PTTCrawler.Log('========== 寄信給 ' + PostAuthor + ' ==========')
                                MailList.append(PostAuthor)
                                
                                if not Test:
                                    
                                    ErrorCode = PTTCrawler.replyPost(Board, Content, PTTCrawler.ReplyPost_Mail, Index=NewPostIndex)
                                    if ErrorCode == PTTCrawler.Success:
                                        PTTCrawler.Log('回文至信箱成功!')
                                        with open('MailList.txt', 'a') as MailListFile:
                                            MailListFile.write(PostAuthor + '\n')
                                    else:
                                        PTTCrawler.Log('回文至信箱失敗 ' + str(ErrorCode))
                            else:
                                PTTCrawler.Log('寄過信了! ' + PostAuthor)
                            '''
                            f = open(str(NewPostIndex) + '_' + NewPost.getPostID() + '.html', 'w', encoding = 'UTF-8')
                            f.write('<html><HEAD>')
                            f.write('<script language=\"javascript\">window.location.href = \"' + NewPost.getWebUrl() + '\";</script>')
                            f.write('<TITLE>Truth\'s PTT Crawler</TITLE></HEAD><body></body></html>')
                            f.close()
                            '''
                            
                            f = open(str(NewPostIndex) + '_' + NewPost.getPostID() + '.txt', 'w', encoding = 'UTF-8')
                            f.write(NewPost.getPostContent())
                            f.close()
                    
                    f = open('LastPostIndex.txt', 'w')
                    f.write(str(NewPostIndex))
                    f.close()
                    
                if Test:
                    PTTCrawler.Log('測試完畢')
                    break
                
            else:
                Log(Board + ' ' + str(LastIndex) + ' 偵測中...', '\r')
                time.sleep(5)
        except KeyboardInterrupt:
            '''
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            '''
            PTTCrawler.Log('Interrupted by user')
            PTTCrawler.logout()
            Retry = False
            break
        except EOFError:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Retry = True
            break
        except ConnectionAbortedError:
            Retry = True
            break
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Retry = True
            break