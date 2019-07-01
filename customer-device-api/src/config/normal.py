class toolsDefine(object):
    def __init__(self):
        self.vpd="/etc/puzzle/vpd/vpdRo"
        self.public="/etc/puzzle/public"

class workDefine(object):
    def __init__(self):
        self.data={
            "config":{"dir":"hwUnit","pythonfile":"config", "classname":"main"},
            "device":{"dir":"hwUnit","pythonfile":"device", "classname":"main"}
        }

class actionDefine(object):
    def __init__(self):
        self.SET=0
        self.GET=1

class resultDefine(object):
    def __init__(self):
        self.NONE=0
        self.PASS=1
        self.FAIL=2
