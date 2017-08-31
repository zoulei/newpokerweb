from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame
import traceback
import time
import threading
import math
import earthmover
import json

lock = threading.Lock()

class WinrateHistogram:
    def __init__(self, winratedata = [], winratestr = ""):
        winratedata.sort(reverse=True)
        if winratestr:
            self.m_data = json.loads(winratestr)
        else:
            self.initdata(winratedata)

    def initdata(self, winratedata):
        slotnum = math.ceil(1 / Constant.HANDSTRENGTHSLOT) + 1
        self.m_data = [0] * int(slotnum)
        for winrate in winratedata:
            self.m_data[int(math.ceil( (1 - winrate) / Constant.HANDSTRENGTHSLOT ) )] += 1

    def __sub__(self, other):
        try:
            return earthmover.EMD(self.m_data,other.m_data)
        except:
            print "WinrateHistogram error : "
            print self.m_data
            print other.m_data
            raise

    def __str__(self):
        return json.dumps(self.m_data)
        # return str(self.m_data)

class BoardHistogram:
    def __init__(self, winratehistogramlist):
        pass

class WinrateEngine(HandsInfo):
    def __init__(self,handsinfo):
        HandsInfo.__init__(self,handsinfo)
        self.m_statekeys = self.m_handsinfo["statekeys"]

        self.m_range = []

    def initprefloprange(self):
        prefloprange = self.m_cumuinfo.m_prefloprange
        for pos, rangenum in enumerate(prefloprange):
            if self.m_cumuinfo.m_inpoolstate[pos] != 0:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(rangenum) )
            else:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(0))

    # test function
    def getbasehistogram(self, ophands):
        board = []
        board.append(hunlgame.Card(2, 2))
        board.append(hunlgame.Card(1, 11))
        board.append(hunlgame.Card(2, 6))

        hand = hunlgame.generateHands("ASJS")
        winratecalculator = hunlgame.SoloWinrateCalculator(board, [hand,], ophands[0], debug=False)
        curwinrate = winratecalculator.calmywinrate()
        # nextturnwinrate = winratecalculator.calnextturnwinrate()
        nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
        winratehistogram = [v[1] for v in nextturnstackwinrate]
        f = open(Constant.CACHEDIR + "tmp","w")
        for board, wr in nextturnstackwinrate:
            writestr = ""
            for card in board:
                writestr += str(card) + " "
            writestr += " " + str(wr) + "\n"
            f.write(writestr)
        f.close()
        return [hand,curwinrate,WinrateHistogram(winratehistogram)]

    # test function
    def printdebuginfo(self,pos,myhands,ophands):
        curboard = self.getcurboard()
        print "board : "
        for v in curboard:
            print v
        print "pos : ", pos
        # print "myhand : ",tmphands[0]
        print "hand len : ", len(myhands),len(ophands[0])
        print "range : ", self.m_cumuinfo.m_prefloprange

    # test function
    def printhistogramdiff(self,handhistogram):
        myhandlen = len(handhistogram)
        for i in xrange(myhandlen):
            printdata = []
            for j in xrange(i + 1, myhandlen):
                handi,winratei,hisi = handhistogram[i]
                handj,winratej,hisj = handhistogram[j]
                printdata.append([handi,winratei,handj,winratej,hisi-hisj])
                # print handi," : ",handj,"      ",hisi-hisj
            printdata.sort(key=lambda v:v[4])
            for handi,winratei,handj,winratej,similarity in printdata:
                print handi," : ",handj,"   --   ",winratei," : ",winratej,"      ",similarity
            raw_input("=================================")

    def calrealwinrate(self, pos):
        curhand = self.gethand(pos)
        if not curhand:
            # myhands = self.m_range[pos]
            return
        else:
            myhands = [curhand,]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        curboard = self.getcurboard()

        # self.printdebuginfo(pos,myhands,ophands)
        if not curboard[-1]:
            return

        # handhistogram = [self.getbasehistogram(ophands)]
        handhistogram = []
        for hand in myhands:
            tmphands = [hand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()
                nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
                winratehistogram = [v[1] for v in nextturnstackwinrate]
                if winratehistogram:
                    handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return

        return handhistogram
        # baseline

        # self.printhistogramdiff(handhistogram)

    def updatecumuinfo(self,round1,actionidx):
        global lock
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            result = self.calrealwinrate(self.m_cumuinfo.m_lastplayer)

            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")

            # lock.acquire()
            f = open(Constant.CACHEDIR + statekey, "a")
            if result and len(result) == 1:
                hand, curwinrate, winratehisobj = result[0]
                f.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), self.m_cumuinfo.m_lastattack,self.getid(),winratehisobj]])+"\n")
            else:
                f.write(Constant.TAB.join([str(v) for v in [-1, self.m_cumuinfo.m_lastattack,self.getid(), -1]]) + "\n")
            f.close()
            # lock.release()

    def test(self):
        self.traversepreflop()
        self.updatecumuinfo(2,0)

class WinrateCalculater(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard >= 0 or showcard == -3):
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

def mainfunc( handsinfo):
    engine = WinrateEngine(handsinfo)
    try:
        engine.test()
    except KeyboardInterrupt:
        raise
    except:
        print handsinfo["_id"]
        traceback.print_exc()

class BoardIdentifierEngine(WinrateEngine):
    def getbasehistogram(self, ophands):
        curboard = []
        curboard.append(hunlgame.Card(2, 2))
        curboard.append(hunlgame.Card(1, 11))
        curboard.append(hunlgame.Card(2, 6))

        # hand = hunlgame.generateHands("ASJS")
        handhistogram = []
        for hand in self.m_range[self.m_cumuinfo.m_lastplayer]:
            tmphands = [hand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()
                nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
                winratehistogram = [v[1] for v in nextturnstackwinrate]
                if winratehistogram:
                    handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return
        return handhistogram

    def calrealwinrate(self, pos):
        myhands = self.m_range[pos]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        boardhistogram = []
        for curboard in hunlgame.Cardsengine().generateallflop():
            handhistogram = []
            for hand in myhands:
                tmphands = [hand,]

                if len(ophands) == 1:
                    winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                    curwinrate = winratecalculator.calmywinrate()
                    nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
                    winratehistogram = [v[1] for v in nextturnstackwinrate]
                    if winratehistogram:
                        handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
                else:
                    # not wrriten yet
                    print "oplen : ",len(ophands)
                    return
            boardhistogram.append([curboard, handhistogram])


if __name__ == "__main__":
    WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="",sync=False).traverse()