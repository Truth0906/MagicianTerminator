
import sys
sys.path.append('../PTTCrawlerLibrary')
import PTT
import json
import re
Debug = False

InterfereSearchList = ['lol', '女僕']

BlockList = ['群', '徵女', '徵妹', '女友', '正妹', '我男', '我是男']
WhiteList = ['老娘', '陪姐', '陪姊', '我是女', 'PO女', '我女']
WantList = ['徵', '想', '希望', '喜歡', '有', '找', '是', '最好', '如果', '來個']

MySelfList = ['我', '原PO', '歲', 'y', '內建', '原波', '關鍵字', '本人', '自己', '元PO']
LocationList = ['台北', '桃園', '新竹', '苗栗', '台中', '彰化', '嘉義', '雲林', '高雄', '屏東', '宜蘭', '花蓮', '台東']
ZodiacSignList = ['巨蟹', '處女', '牡羊', '金牛', '天秤', '雙魚', '雙子', '摩羯', '獅子', '射手', '水瓶', '天蠍']

GirlList = ['女', '妹', 'female', '姐', '姊', 'ol']

SplitTargetList = ['跟', '和', '~', '，', '～', '的', '：', '追']

def showDebugLine(Index):
    if Debug:
        print('Return at ' + str(Index))
def showDebugMessage(Message):
    if Debug:
        print('Debug: ' + Message)
        
def splitList(List, Target):
    result = []
    for Temp in List:
        result.extend(Temp.split(Target))
    return result
def needStore(Post):

    Content = Post.getPostContent().lower()
    
    for InterfereSearchWord in InterfereSearchList:
        Content = Content.replace(InterfereSearchWord, '')
    
    for BlockWord in BlockList:
        if BlockWord.lower() in Content:
            showDebugMessage(BlockWord)
            showDebugLine(1)
            return False
        if BlockWord.lower() in Post.getTitle().lower():
            showDebugMessage(BlockWord)
            showDebugLine(1.1)
            return False
        
    for WhiteWord in WhiteList:
        if WhiteWord.lower() in Content:
            showDebugLine(2)
            return True
        if WhiteWord.lower() in Post.getTitle().lower():
            showDebugLine(2.1)
            return True

    #Analysis content
    
    TargetList = Content.splitlines()
    for WantWord in WantList:
        for Target in TargetList:
            if WantWord in Target:
                showDebugMessage('移除: ' + Target)
                TargetList.remove(Target)
    
    for SplitTarget in SplitTargetList:
        TargetList = splitList(TargetList, SplitTarget)
    
    for Target in reversed(TargetList):
        if len(Target) == 0:
            continue
        showDebugMessage(Target)
        
        for ZodiacSign in ZodiacSignList:
            for Girl in GirlList:
                if ZodiacSign.lower() in Target.lower():
                    #print(Target)
                    Target = Target.lower().replace(ZodiacSign.lower(), '')
                    #print(Target)
                else:
                    continue
                if Girl.lower() in Target.lower():
                    showDebugLine(5.3)
                    return True
        
        for Location in LocationList:
            for Girl in GirlList:
                if Location.lower() in Target.lower() and Girl.lower() in Target.lower():
                    showDebugLine(5.2)
                    return True
                    
        isSelf = False
        for Me in MySelfList:
            for Girl in GirlList:
            
                if not Me.lower() in Target.lower():
                    continue
                isSelf = True
                if not Girl.lower() in Target.lower():
                    continue
                if Target.lower().find(Me.lower()) < Target.lower().find(Girl.lower()):
                    showDebugLine(8)
                    return True
        if isSelf:
            showDebugLine(8.9)
            return False
        
        for Girl in GirlList:
            if Girl.lower() in Target.lower() and len(Target) < len(Girl) + 2:
                #print(len(Girl))
                #print(len(Target))
                showDebugLine(8.1)
                return True
        
        NumberList = re.findall(r'\d+', Target)
        #print(NumberList)
        if len(NumberList) > 0:
            for Girl in GirlList:
                if Girl.lower() in Target.lower():
                    showDebugLine(9)
                    return True
    showDebugLine(100)
    return False
if __name__ == '__main__':
    Debug = True
    Board = 'Wanted'
    TestPostID = ['1PWK2g56', '1PWJEL4a', '1PWOHEKU', '1PWBDDK4', '1PWcM3d8', '1PWRagRV', '1PWWDtDh', '1PWTvCqf',
    '1PWfVQtH',
    '1PWhGd0i',
    '1PWrtU7V',
    '1PWu2Kl5',
    '1PWx89bh',
    '1PX76x-S',
    ]
    
    # Define your id and password
    
    try:
        with open('Account.txt', encoding = 'utf-8-sig') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
        print('Auto ID password mode')
    except FileNotFoundError:
        ID = input('Input ID: ')
        Password = getpass.getpass('Input password: ')
    
    PTTCrawler = PTT.Crawler(ID, Password, False)
    if not PTTCrawler.isLoginSuccess():
        pass
    else :    
        for PostID in TestPostID:
            ErrorCode, NewPost = PTTCrawler.getPostInfoByID(Board, PostID)
            if ErrorCode == PTTCrawler.PostDeleted:
                PTTCrawler.Log('Post has been deleted')
                continue
            if ErrorCode == PTTCrawler.WebFormatError:
                PTTCrawler.Log('Web structure error')
                continue
            if ErrorCode != PTTCrawler.Success:
                PTTCrawler.Log('Get post by ID fail')
                continue
            if NewPost == None:
                PTTCrawler.Log('Post is empty')
                continue
                
            if needStore(NewPost):
                print(PostID + ' true')
            else:
                print(PostID + ' false')
        PTTCrawler.logout()