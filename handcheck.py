from handsengine import HandsInfo
from TraverseHands import TraverseHands
import DBOperater
import Constant
import traceback
import handsinfoexception
import handsinfocommon

class LastAllinErrorChecker(HandsInfo):
    def updatecumuinfo(self,round,actionidx):
        try:
            HandsInfo.updatecumuinfo(self,round,actionidx)
        except handsinfoexception.AllinWithExtraChips as e:
            if self.islastaction(round,actionidx):
                raise handsinfoexception.LastActionAllinError
            else:
                raise
        except:
            raise

class CheckHand(TraverseHands):
    def __init__(self,db,clt,handsid=""):
        TraverseHands.__init__(self, db, clt, handsid)
        self.m_cnt = 0

    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if showcard == -3 or showcard >= 0:
            return False
        return True

    def mainfunc(self, handsinfo):
        handsobj = LastAllinErrorChecker(handsinfo)
        try:
            handsobj.traversealldata()
            if not handsobj.m_cumuinfo.isgameover():
                print handsobj.m_cumuinfo.m_curturn,handsobj.m_cumuinfo.m_curturnover,handsobj.m_cumuinfo.m_remainplayer
                print handsobj.m_cumuinfo.getlastactioner(),handsobj.m_cumuinfo.m_lastplayer
                raise handsinfoexception.NotEnoughAction()
        except Exception as e:
            print handsobj.m_handsinfo["_id"]
            print "Exception : " + str(e)
            # print traceback.print_exc()
            # traceback.print_exc()
            handsobj.m_handsinfo["showcard"] = -4
            handsinfocommon.pp.pprint(handsinfo)
            DBOperater.ReplaceOne(self.m_db,self.m_clt,{"_id":handsinfo["_id"]},handsobj.m_handsinfo)
            self.m_cnt += 1
            print "\n\n"

if __name__ == "__main__":
    v = CheckHand(Constant.HANDSDB, Constant.TJHANDSCLT)
    v.traverse()
    print v.m_cnt