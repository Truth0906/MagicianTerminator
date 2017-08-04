
import sys
sys.path.append('../PTTCrawlerLibrary')
import PTT

#AllBlackList = [u"徵女", u"徵求女", u"我男", u"我大叔", u"原PO 男", u"原PO 難", u"找女", u"四輪", u"聊天群", u"群組", u"直接加", u"哥", u"賴群", u"雄性", "man"]
#TitleBlackList = [u"女", u"妳", u"妹", u"問安", u"公告"]
#ContentBlackList = [u"5566"]

Debug = False

AllBlackList = [u"徵女", u"徵求女", u"我男", u"我大叔", u"原PO 男", u"原PO 難", u"找女", u"四輪", u"聊天群", u"群組", u"直接加", u"哥", u"賴群", u"小弟", u"[公告]", u"妳"]
TalkList = [u"聊", "line", u"賴", u"說話"]
GirlList = [u"女", u"妹", "female"]
BoyList = [u"男", u"man", u"叔", u"雄性", u"哥", "male"]
WantList = [u"徵", u"想", u"來個", u"希望"]
MySelfList = [u"我", u"原PO", u"歲", "y"]
LocationList = [u"台北", u"桃園", u"新竹", u"苗栗", u"台中", u"彰化", u"嘉義", u"雲林", u"高雄", u"屏東", u"宜蘭", u"花蓮", u"台東"]
ZodiacSignList = [u"巨蟹", u"處女", u"牡羊", u"金牛", u"天秤", u"雙魚", u"雙子", u"摩羯", u"獅子", u"射手", u"水瓶", u"天蠍"]
def showDebugLine(Index):
    if Debug:
        print("Return at " + str(Index))
def showDebugMessage(Message):
    if Debug:
        print("Debug: " + Message)
def needStore(Post):

    for Black in AllBlackList:
        if Black in Post.getPostContent().lower() or Black in Post.getTitle().lower():
            showDebugLine(4)
            return False

    if not u"徵求" in Post.getTitle():
        showDebugLine(1)
        return False
        
    for Target in GirlList:
        if u"徵求" in Post.getTitle() and Target in Post.getTitle():
            showDebugLine(2)
            return False
    #Analysis content
    
    isTalkPost = False
    for TalkTarget in TalkList:
        if TalkTarget in Post.getPostContent().lower() or TalkTarget in Post.getTitle().lower():
            isTalkPost = True
            break
            
    if not isTalkPost:
        showDebugLine(3)
        return False
    
    for TargetA in Post.getPostContent().splitlines():
        for TargetB in TargetA.split("~"):
            for Target in TargetA.split(u"，"):
                showDebugMessage(Target)
                for Location in LocationList:
                    for Girl in GirlList:
                        if Location in Target.lower() and Girl in Target.lower():
                            showDebugLine(5.2)
                            return True
                    for Boy in BoyList:
                        if Location in Target.lower() and Boy in Target.lower():
                            showDebugLine(5.1)
                            return False
                for ZodiacSign in ZodiacSignList:
                    for Girl in GirlList:
                        if ZodiacSign in Target.lower() and Girl in Target.lower():
                            showDebugLine(5.3)
                            return True
                    for Boy in BoyList:
                        if ZodiacSign in Target.lower() and Boy in Target.lower():
                            showDebugLine(5.4)
                            return False
                for Want in WantList:
                    if Want in Target.lower():
                        for Girl in GirlList:
                            if Girl in Target.lower():
                                showDebugLine(6.1)
                                return False
                        for Boy in BoyList:
                            if Boy in Target.lower():
                                showDebugLine(6.2)
                                return True
                for Me in MySelfList:
                    for Girl in GirlList:
                        if Me in Target.lower() and Girl in Target.lower():
                            showDebugLine(8)
                            return True
                    for Boy in BoyList:
                        if Me in Target.lower() and Boy in Target.lower():
                            showDebugLine(7)
                            return False
if __name__ == "__main__":
    Debug = True
    Board = "Wanted"
    TestPostID = ["1PC5cYPm"]
    
    # Define your id and password
    
    ID = 'QQ'
    Password = '><'
    
    PTTCrawler = PTT.Crawler(ID, Password, False)
    if not PTTCrawler.isLoginSuccess():
        pass
    else :    
        for PostID in TestPostID:
            ErrorCode, NewPost = PTTCrawler.getPostInfoByID(Board, PostID)
            if ErrorCode == PTT.PostDeleted:
                PTTCrawler.Log('Post has been deleted')
                continue
            if ErrorCode == PTT.WebFormatError:
                PTTCrawler.Log('Web structure error')
                continue
            if ErrorCode != PTT.Success:
                PTTCrawler.Log('Get post by index fail')
                continue
            if NewPost == None:
                PTTCrawler.Log('Post is empty')
                continue
                
            if needStore(NewPost):
                print(PostID + " true")
            else:
                print(PostID + " false")
        PTTCrawler.logout()