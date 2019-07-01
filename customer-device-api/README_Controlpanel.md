## Control Panel
### device use
app.add_url_rule('/puzzle/api/v1/devCPInfo', 'devCPInfo', self.devCPInfo, methods=['GET'])
app.add_url_rule('/puzzle/api/v1/devPower', 'devPower', self.devPower, methods=['POST'])
### pc use
app.add_url_rule('/puzzle/api/v1/devNetworkInfo', 'devNetworkInfo', self.devNetworkInfo, methods=['GET'])
app.add_url_rule('/puzzle/api/v1/devCheck', 'devCheck', self.devCheck, methods=['POST'])

#### http://10.10.70.159:8882/puzzle/api/v1/devPower
#### POST
#### BODY
```
{  "power":"reboot" }

or

{  "power":"off" }
```
#### RESP
```
{"result":"success"}

or

{"result": "fail" }
```

#### http://10.10.70.159:8882/puzzle/api/v1/devCPInfo
#### GET
#### RESP
```
{
    "cpu": "x86_64 CPU(s): 12",
    "firmwarever": "0.0.2-beta",
    "memory": "15.58 GB (14.36 GB free)",
    "productname": "PUZZLE-IN001",
    "serialno": "Q189M00030"
}
```

#### http://10.10.70.159:8882/puzzle/api/v1/devCheck
#### POST
#### BODY
```
{
	"ip":"192.168.0.1"
}
```
#### RESP
```
{
    "firmwarever": "0.0.2-beta",
    "interfaces": 8,
    "modelName": "PUZZLE-IN001",
    "msg": "I am Puzzle!",
    "sn": "Q189M00030"
}
```

#### http://10.10.70.159:8882/puzzle/api/v1/devNetworkInfo
#### GET
#### RESP
```
[
    {
        "description": "Ethernet Interface",
        "interface": "docker0",
        "ip": "172.17.0.1",
        "macaddr": "02:42:51:a7:92:63",
        "status": "DOWN",
        "type": "Virtual"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp10s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:9a",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp3s0",
        "ip": "10.10.70.159",
        "macaddr": "e0:18:7d:2e:ca:93",
        "status": "UP",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp4s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:94",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp5s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:95",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp6s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:96",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp7s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:97",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp8s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:98",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "enp9s0",
        "ip": " ",
        "macaddr": "e0:18:7d:2e:ca:99",
        "status": "DOWN",
        "type": "Physical"
    },
    {
        "description": "Ethernet Interface",
        "interface": "lo",
        "ip": "127.0.0.1",
        "macaddr": "unknown",
        "status": "UNKNOWN",
        "type": "Virtual"
    }
]
```
