import Constant
import handsinfocommon
import copy
import prefloprange

# this class do not consider the real seat number
class CumuInfo:
    def __init__(self, playerquantity, bbvalue, anti, stacksize):
        self.m_playerquantity = playerquantity
        self.m_bb = bbvalue
        self.m_anti = anti
        self.m_stacksize = stacksize
        self.reset()

        self.m_handsrangeobj = prefloprange.prefloprangge()

    # this function is called after the preflop is over
    def getpreflopinfomation(self):
        return {
            "range" :   self.m_prefloprange,
            "raiser"    :   self.m_preflopraiser,
            "betlevel"  :   self.m_preflopbetlevel
        }

    # this function is called after the action is updated
    def getlastaction(self):
        return [self.m_lastaction,self.m_lastattack]

    # this fucntion is called after the action is updated to get the state before the last action is updated
    def getlaststate(self):
        return self.m_laststate
    #           {
    #             "pos":pos,
    #             "relativepos":relativepos,
    #             "remain":self.m_remainplayer-self.m_allinplayer,
    #             "normalneedtobet":normalneedtobet,
    #             "normalpayoff":normalpayoff,
    #             "betbb":betbb,
    #             "circle":self.m_circle
    #             }

    def reset(self):
        # pot size
        self.m_pot = self.m_bb + self.m_bb/2 + self.m_anti * self.m_playerquantity

        # raiser of the current turn
        # 0 means no raiser
        self.m_raiser = 0
        self.m_fakeraiser = 0

        # raiser of the preflop
        # 0 means no raiser
        self.m_preflopraiser = 0

        # how many bets, 0 means check
        self.m_betlevel = 1

        # how many bet pot, records the preflop information
        self.m_preflopbetlevel = 0

        # how many stake the raiser bet
        self.m_betvalue = self.m_bb

        # how many stake does the raiser raise
        self.m_raisevalue = self.m_bb

        # the betting circle of the current turn
        self.m_circle = 1

        # bet history of the current turn
        self.m_bethistory = {Constant.BBPOS:self.m_bb, Constant.SBPOS:self.m_bb / 2}

        # real time state of every player
        # 0 means fold or not in game,
        # 1 means playing
        # 2 means all in
        self.m_inpoolstate = {}

        # action sequence of after flop
        self.m_afterflopposlist = {}
        # action sequence of pre flop
        self.m_preflopposlist = {}

        # the last player that have taken action
        self.m_lastplayer = 0

        # the next player to take action
        # this value doesnot necessary means anything when the game has finished
        # -1 means game over
        self.m_nextplayer = self.m_preflopposlist[0]

        self.initinpoolstate()

        # 0 means preflop
        self.m_curturn = 0

        # if current turn has finished
        self.m_curturnover = False

        # remaining player, including those all in
        self.m_remainplayer = self.m_playerquantity

        # all in player
        self.m_allinplayer = 0

        # # how many stake the next player need to bet at least
        self.m_tmpstacksize = copy.deepcopy(self.m_stacksize)


        self.m_lastaction = 0
        self.m_lastattack = 0

        self.m_laststate = {}

        # 1. player's range. 2. betlevel. 3. player number and relative pos. 4. raiser. 5. pot. 6. how many player all in.
        self.m_prefloprange = [-1] * 10


    def initinpoolstate(self):
        self.m_inpoolstate = [0]*10
        self.m_afterflopposlist = range(self.m_playerquantity - 2,0, -1)
        self.m_preflopposlist = [9,8] + range(self.m_playerquantity - 2,0, -1)
        self.m_afterflopposlist.extend([9,8])
        for pos in self.m_afterflopposlist:
            self.m_inpoolstate[pos] = 1

    def newturn(self):
        if self.m_curturn == -1:
            return

        if self.m_curturn == 0:
            self.m_preflopraiser = self.m_raiser
            self.m_preflopbetlevel = self.m_betlevel

        self.m_curturn += 1
        self.m_curturnover = False
        self.m_raiser = 0
        self.m_fakeraiser = 0
        self.m_betlevel = 0
        self.m_circle = 1
        self.m_betvalue = 0
        self.m_bethistory = {}
        self.m_needtobet = 0
        self.m_lastplayer = 0

        self.m_lastattack = 0


    def getnextplayer(self):
        if self.m_curturnover:
            if self.m_curturn + 1 > 0:
                poslist = self.m_afterflopposlist
            else:
                poslist = self.m_preflopposlist
            for pos in poslist:
                if self.m_inpoolstate[pos] == 1:
                    return pos
                if self.m_raiser == pos:
                    return pos
            else:
                # every one all in or fold
                return -1
        else:
            lastplayerindex = self.m_afterflopposlist.index(self.m_lastplayer)
            for pos in self.m_afterflopposlist[lastplayerindex + 1:] + self.m_afterflopposlist[:lastplayerindex + 1]:
                if self.m_inpoolstate[pos] == 1:
                    return pos
                if self.m_fakeraiser:
                    if self.m_fakeraiser == pos:
                        return pos
                elif self.m_raiser == pos:
                    return pos
            else:
                # every one all in or fold
                return -1

    # the last player to action in the current turn and the current round
    def getlastactioner(self):
        if self.m_curturn == 0:
            poslist = self.m_preflopposlist
        else:
            poslist = self.m_afterflopposlist
        for idx in xrange(len(poslist), -1, -1):
            pos = poslist[idx]
            if self.m_inpoolstate[pos] == 1:
                return pos

    def updatecurturnstate(self):
        if self.m_raiser == 0:
            # no raiser
            if self.getlastactioner() == self.m_lastplayer:
                self.m_curturnover = True
            else:
                self.m_curturnover = False
        elif self.m_fakeraiser == 0:
            # has raiser and no invalid raise
            if self.getnextplayer() == self.m_raiser:
                self.m_curturnover = True
            else:
                self.m_curturnover = False
        else:
            # has invalid raise
            if self.getnextplayer() == self.m_fakeraiser:
                self.m_curturnover = True
            else:
                self.m_curturnover = False

    def isgameover(self):
        if self.m_curturnover == False:
            return False

        remain = self.m_remainplayer - self.m_allinplayer
        if remain > 1:
            return False
        elif remain == 1:
            return True
        elif remain == 0:
            return True
        else:
            print "remain small than 0"
            raise

    def update(self,action,value):
        if self.isgameover():
            print "game has over"
            raise
        if self.m_curturnover:
            self.newturn()
        self.m_laststate = self.calstatistics()
        self.updatestate(action,value)
        self.updatecircle()
        self.m_lastplayer = self.m_nextplayer
        self.updatecurturnstate()
        self.m_nextplayer = self.getnextplayer()
        self.updateprefloprange()
        # if not self.isgameover() and self.m_curturnover:
        #     self.newturn()

    def updatecircle(self):
        if self.m_lastplayer == 0:
            self.m_circle = 1
        if self.m_curturn == 0:
            poslist = self.m_preflopposlist
        else:
            poslist = self.m_afterflopposlist
        lastidx = poslist.index(self.m_lastplayer)
        nextidx = poslist.index(self.m_nextplayer)
        if lastidx > nextidx:
            self.m_circle += 1

    # 0 means raiser is totally invalid, since all other has all in
    def calvalidraisevalue(self, pos, value):
        validraisevalue = 0
        for idx in self.m_afterflopposlist:
            if idx == pos:
                continue
            if self.m_inpoolstate[idx] == 1:
                targetstack = self.m_bethistory[idx] + self.m_stacksize[idx]
                if targetstack >= value:
                    validraisevalue = value
                    break
                else:
                    if targetstack > validraisevalue:
                        validraisevalue = targetstack
        return validraisevalue

    def updatestate(self,action,value):
        pos = self.m_nextplayer

        if action == 2:
            value = self.calvalidraisevalue(pos, value)
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 3
        elif action == 4 and value > self.m_betvalue:
            value = self.calvalidraisevalue(pos, value)
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 3

        if value > self.m_betvalue:
            givepayoff = (value + self.m_pot - self.m_bethistory.get(pos,0)) * 1.0 / ( value - self.m_betvalue)
            givepayoff = handsinfocommon.roundhalf(givepayoff)
            self.m_lastattack = self.m_betlevel + 1 + givepayoff * 0.1
        else:
            self.m_lastattack = 0

        if action == 1 or action == -1:
            # curstate["fold"] += 1
            self.m_inpoolstate[pos] = 0
            self.m_remainplayer -= 1
            self.m_lastaction = 1

        elif action == 2:
            self.m_lastaction = 2
            # curstate["raise"] += 1
            self.m_betlevel += 1
            self.m_raisevalue = value - self.m_betvalue
            if (self.m_betvalue >= value):
                print "betvalue >= value"
                raise
            self.m_betvalue = value
            self.m_pot += value -self.m_bethistory.get(pos,0)
            self.m_tmpstacksize -= value -self.m_bethistory.get(pos,0)
            self.m_raiser = pos
            self.m_fakeraiser = 0

            self.m_bethistory[pos] = value

        elif action == 3 or action == 6:
            self.m_lastaction = action
            # curstate["call"] += 1
            self.m_pot += self.m_betvalue-self.m_bethistory.get(pos,0)
            self.m_tmpstacksize -= self.m_betvalue-self.m_bethistory.get(pos,0)
            self.m_bethistory[pos] = self.m_betvalue

        elif action == 4:
            self.m_allinplayer += 1
            if value <= self.m_betvalue:
                # curstate["call"] += 1
                self.m_lastaction = 4.3

            else:
                if value - self.m_betvalue < self.m_raisevalue:
                    # invalid raise
                    self.m_fakeraiser = pos
                    # self.m_betvalue = value
                else:
                    # valid raise
                    self.m_raiser = pos
                    self.m_fakeraiser = 0
                    self.m_raisevalue = value - self.m_betvalue

                givepayoff = (value + self.m_pot - self.m_bethistory.get(pos,0)) * 1.0 / ( value - self.m_betvalue)
                givepayoff = handsinfocommon.roundhalf(givepayoff)
                if givepayoff <= 3:
                    # curstate["raise"] += 1
                    self.m_lastaction = 4.2
                    self.m_betlevel += 1
                else:
                    self.m_lastaction = 4.3
                    # curstate["call"] += 1
                self.m_betvalue = value
            self.m_pot += value-self.m_bethistory.get(pos,0)
            self.m_tmpstacksize -= value-self.m_bethistory.get(pos,0)
            self.m_bethistory[pos] = value
        elif action == 12:
            self.m_lastaction = 12
            for idx in xrange(len(self.m_inpoolstate)):
                if idx != pos:
                    self.m_inpoolstate[idx] = 0
            self.m_remainplayer = 1
            self.m_allinplayer = 0
            self.m_curturnover = True

    # this function is called before the action is updated
    def calstatistics(self):
        bb = self.m_bb
        pos = self.m_nextplayer

        # needtobet, payoffrate, pos, relativepos,
        if self.m_bethistory.get(self.m_nextplayer,0) + self.m_stacksize[self.m_nextplayer] < self.m_betvalue:
            # need to call all in
            needtobet = self.m_stacksize[self.m_nextplayer]
            curturnstack = needtobet + self.m_bethistory.get(pos,0)
            if needtobet < bb:
                needtobet = bb

            if needtobet != 0:
                # seppot = self.m_anti * self.m_playerquantitiy + bb + bb / 2
                seppot = self.m_pot
                for hispos,hisbetvalue in self.m_bethistory.items():
                    if hisbetvalue > curturnstack:
                        seppot -= hisbetvalue - curturnstack

                payoffrate = seppot * 1.0 / needtobet
            else:
                payoffrate = 10000

            # since call all in, betbb depends on his remaining stack, NOT the real betbb
            if curturnstack < bb:
                betbb = int((bb + 0.5 * bb) / bb)
            else:
                betbb = int((curturnstack + 0.5 * bb) / bb)

        else:
            needtobet = self.m_betvalue - self.m_bethistory.get(pos,0)
            if needtobet != 0:
                payoffrate = self.m_pot * 1.0 / needtobet
            else:
                payoffrate = 10000

            betbb = int((self.m_pot + 0.5 * bb) / bb)

        normalpayoff = int(round(payoffrate * 2)) * 5
        normalneedtobet = int( (needtobet + 0.5 * bb) / bb )

        if self.m_curturn == 0:
            if pos > self.m_raiser:
                relativepos = 0
            else:
                relativepos = 1
        else:
            if pos > self.m_raiser:
                relativepos = 0
            elif pos < self.m_raiser:
                relativepos = 1
            else:
                # raiser
                relativepos = 2

        realpos = 0
        for idx in self.m_inpoolstate:
            if self.m_inpoolstate[idx] == 1:
                realpos += 1
            if idx == pos:
                break

        return {
                "pos":pos,
                "relativepos":relativepos,
                "remain":self.m_remainplayer-self.m_allinplayer,
                "allin":self.m_allinplayer,
                "normalneedtobet":normalneedtobet,
                "normalpayoff":normalpayoff,
                "betbb":betbb,
                "circle":self.m_circle,
                "betlevel":self.m_betlevel,
                "round":self.m_curturn,
                "raiser":self.m_raiser,
                }

    # update preflop state
    # preflop state include :
    # 1. player's range. 2. betlevel. 3. player number and relative pos. 4. raiser. 5. pot. 6. how many player all in.
    def updateprefloprange(self):
        if self.m_laststate["round"] != 1:
            return
        if self.m_laststate["circle"] == 1:
            newrange = self.m_handsrangeobj.getrange(self.m_laststate["circle"],self.m_laststate["betlevel"],
                                          self.m_laststate["pos"],self.m_laststate["betbb"],self.m_laststate["normalpayoff"],
                                          self.actiontransfer(self.m_lastaction) )
        elif self.m_laststate["circle"] > 1:
            newrange = self.m_handsrangeobj.getrange(self.m_laststate["circle"],self.m_laststate["betlevel"],
                                          self.m_laststate["relativepos"],self.m_laststate["normalneedtobet"],self.m_laststate["normalpayoff"],
                                          self.actiontransfer(self.m_lastaction) )

        if newrange:
            self.m_prefloprange[self.m_laststate["pos"]] = newrange

    # self.m_preflopstate = {
    #         "range" :   [-1]*10,
    #         "betlevel"  :   1,
    #         "playernum"    :   self.m_playerquantity,
    #         "relativepos"   :   2,  # 2 means no raiser,
    #         "raiser"    :   0,
    #         "pot"   :   self.m_pot,
    #         "allin"    :   0,
    #     }

    def actiontransfer(self,action):
        if action == 1:
            return "fold"
        elif action == 12:
            return
        elif action in [2,4.2]:
            return "raise"
        elif action in [3,6,4.3]:
            return "call"



















class HandsInfo:
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo
        self.m_playerquantitiy = 0
        self.m_showcard = 0

        self.m_cumuinfo = CumuInfo()
        self.init()

    def init(self):
        self.m_playerquantitiy = len(self.m_handsinfo["data"][0][2])

        # -3 means fail to record showcard
        # -1 or -2 means record error, this hands is not usefull
        # 0 means game over in advance
        # 1 means game over with showcard
        self.m_showcard = self.m_handsinfo["showcard"]

    def getplayerquantity(self):
        return self.m_playerquantitiy

    def isvalid(self):
        if not (self.m_showcard >= 0 or self.m_showcard == -3):
            return False
        return True

    # return how far does this game go for
    # 1 - 4 means preflop to river
    def getturncount(self):
        handsdata = self.m_handsinfo["data"]
        infolen = len(handsdata)
        if infolen < 6:
            # over before river
            return infolen - 2
        elif infolen == 7:
            # play to river or all in at turn
            if handsdata[4]==None:
                # all in at turn
                return 3
            else:
                # play to river
                return 4
        else:
            # infolen == 6
            # may be play to river and not show card
            # may be all in before river
            if not isinstance(handsdata[5][0][0],list):
                # play to river and not show card
                return 4

            for idx in xrange(4,0,-1):
                # all in before river
                if handsdata[idx]!= None:
                    return idx - 1

    def getpreflopbetdata(self):
        return self.m_handsinfo["data"][1]

    def getflopbetdata(self):
        return self.m_handsinfo["data"][2]

    def getturnbetdata(self):
        return self.m_handsinfo["data"][3]

    def getriverbetdata(self):
        return self.m_handsinfo["data"][4]

    def getrounddata(self, round):
        return self.m_handsinfo["data"][round + 1]

    def getboard(self):
        handsdata = self.m_handsinfo["data"]
        infolen = len(handsdata)
        if infolen < 6:
            # over before river
            return handsdata[-1]
        elif infolen == 7:
            # play to river or all in at turn
            return handsdata[-1]

        else:
            # infolen == 6
            # may be play to river and not show card
            # may be all in before river
            if not isinstance(handsdata[5][0][0],list):
                # play to river and not show card
                return handsdata[-1]

            for idx in xrange(4,0,-1):
                # all in before river
                if handsdata[idx]!= None:
                    return handsdata[idx]

    def getprivatecard(self):
        if self.m_showcard > 0 or self.m_showcard == -3:
            return self.m_handsinfo["data"][5]
        else:
            return None



    # round starts from 0, which means preflop
    # actionidx starts from 0, which means the first action
    def getcumuinfo(self,round, actionidx):
        if round == 0 and actionidx == 0:
            self.m_cumuinfo.reset()

        action, value = self.getrounddata(round)[actionidx]
        self.m_cumuinfo.update(action, value)
        return self.m_cumuinfo
