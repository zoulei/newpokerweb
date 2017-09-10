from handsengine import HandsInfo
from afterflopwinrate import WinrateEngine, FnameManager
from TraverseHands import TraverseHands
import hunlgame
import math
from pickleengine import PickleEngine
import Constant

class FirstTurnBetData:
    def __init__(self, winrate, attack, iswin):
        self.m_winrate = winrate
        self.m_attack = attack
        self.m_iswin = iswin
        if not attack and not iswin:
            self.m_attack = -1
            self.m_iswin = 1

    def __str__(self):
        return "\t".join([self.m_winrate,self.m_attack,self.m_iswin])

class FTBetdataEngine(WinrateEngine):
    def __init__(self,handsinfo):
        WinrateEngine.__init__(self,handsinfo)
        self.m_attack = 0

    def calbetdata(self):
        curboard = self.getcurboard()

        if not curboard[-1]:
            return

        myhands = [self.gethand(self.m_cumuinfo.m_lastplayer),]
        ophands = []
        for pos,inpool in enumerate(self.m_cumuinfo.m_inpoolstate):
            if inpool == 1 and pos != self.m_cumuinfo.m_lastplayer:
                ophands.append(self.gethand(pos))

        winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands,debug=False)
        iswin = winratecalculator.calmywinrate()

        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == self.m_cumuinfo.m_lastplayer:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        if len(ophands) == 1:
            winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands[0],debug=False)
            curwinrate = winratecalculator.calmywinrate()

            return FirstTurnBetData(curwinrate,self.m_attack ,iswin)

    def updateattackinfo(self):
        tmpattack = self.m_cumuinfo.m_lastattack
        while tmpattack > 2:
            tmpattack -= 1
        if tmpattack:
            self.m_attack = math.ceil(self.m_attack) + tmpattack

    def updatecumuinfo(self,round1,actionidx):
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 == 1:
            return
        if self.m_cumuinfo.m_lastaction not in [2,4.2]:
            return

        self.updateattackinfo()
        betdata = self.calbetdata()
        if betdata is None:
            return

        PickleEngine.tempdump(betdata,  FnameManager().generateftbetdatatempfname(self.getpreflopstatekey(), self.getid(),round1,actionidx))

class TraverseFTBetdata(TraverseHands):
    def filter(self, handsinfo):
        if handsinfo["showcard"] != 1:
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        return False

    def traverse(self):
        TraverseHands.traverse(self)

        fnamemanagerobj = FnameManager()
        PickleEngine.combine(fnamemanagerobj.getftbetdatatempfnamerawstatekey, fnamemanagerobj.generateftebetdatafname )

def mainfunc(handsinfo):
    FTBetdataEngine(handsinfo).traversealldata()

def testbetinfo():
    betinfolist = PickleEngine.load(Constant.CACHEDIR + "")
    for v in betinfolist:
        print v

class BetinfoClassifier:
    def __init__(self, datafname):
        self.m_datafname = datafname
        self.m_betvaluerange = [-1, 0, 1, 2, 3, 4]
        self.m_classifyvalue = [0] * len(self.m_betvaluerange)

    def classify(self):
        self.m_data = PickleEngine.load(self.m_datafname)

        for idx, betvalue in enumerate(self.m_betvaluerange[:-1]):
            start = self.m_classifyvalue[idx]
            leasterror = len(self.m_data)
            leastvalue = start
            for classifyvalue in xrange(start, 1, 0.01):
                curerror = self.geterror(classifyvalue, betvalue)
                if curerror < leasterror:
                    leasterror = curerror
                    leastvalue = classifyvalue
            self.m_classifyvalue[idx + 1] = leastvalue

        return self.m_classifyvalue

    def geterror(self, classifyvalue, betvalue):
        error = 0
        for data in self.m_data:
            if data.m_attack != betvalue:
                continue
            if data.m_winrate <= classifyvalue:
                # in range
                if not data.m_iswin:
                    error += 1
            else:
                # out range
                if data.m_iswin:
                    error += 1
        return error

if __name__ == "__main__":
    TraverseFTBetdata(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="",sync=False,step=100,start=0,end=1).traverse()
    testbetinfo()
    # BetinfoClassifier(Constant.CACHEDIR + "")