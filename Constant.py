MONGOHOST = '192.168.112.111'
#MONGOHOST = 'localhost'
MONGOPORT = 27017
DBUSERNAME = 'root'
DBPWD = "123459"
AUTHDBNAME = "admin"

LOGINDB = "pmdb"
LOGINCLT = "loginclt"

HANDSDB = "handsdb"
HANDSCLT = "handsclt"

RAWHANDSCLT = "rawhandsclt"
HISHANDSCLT = "hishandsclt"
TJHISHANDSCLT = "tjhishandsclt"
TJHANDSCLT = "tjhandsclt"

GAMESEQCLT = "gameseqclt"

CUMUCLT = "cumuclt"

# =====================preflop state related=============================
PREFLOPRANGEDOC = "prefloprange"
FTDATA = "ftdata"

JOINRATEDATA = "joinratedata"
REPAIRJOINRATE = "repairjoinrate"

UPLOAD_FOLDER = '/mnt/mfs/users/zoul15/pmimg/'
OCR_ERROR_FOLDER = "/mnt/mfs/users/zoul15/errorimg/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

NAMEIMGPREFIX = "shotname"

HANDSTHRE = 100
STATETHRE = 1

BELIEVERATE = 60
FILTERHANDS = 20

# ========================game level related=============================
BB = 10
ANTI = 2

# ========================cache data related=============================
CACHEDIR = "data/"
AFTERFLOPSTATEHEADER = CACHEDIR + "afterflopstateheader"
AFTERFLOPSTATEDATA = CACHEDIR + "afterflopstatedata"

# ========================hands strength related=====================
COMPLETESTRENGTHMAPPREFIX = CACHEDIR + "strengthmap"
REVERSECOMPLETESTRENGTHMAPPREFIX = CACHEDIR + "reversestrengthmap"

# ========================symbol======================================
TAB = "\t"
SPACE = " "
DOT = ","

