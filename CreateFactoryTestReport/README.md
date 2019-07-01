# API for generating Factory Test Report PDF

### API details 

Link: http://localhost:6662/puzzle/api/v1/create_report

Method: POST

### Query
```
data = {
    "serialNo": "Q18AM00060",
    "deviceInfo": {
	"CPU": "24105-12021002-02-RS|RX-421BD|1",
	"Memory": "",
	"DDR4": 0,
	"NGFF": 0,
	"PCIEX4": 0,
	"RJ45": 0,
	"SATA": 0,
	"USB3_0": 0,
	"USB2_0": 0,
	"mSATA": 0,
	"SIM": 0,
	"RedundantPower": 0,
	"TPM": 0,
	"LCM": 0,
	"DeviceModel": ""
    },
    "macInfo": [
	{
	    "interface": "MAC1",
	    "macaddr": "00187DFF1A9D"
	},
	{
	    "interface": "MAC2",
	    "macaddr": "00187DFF1A9E"
	},
	{
	    "interface": "MAC3",
	    "macaddr": "00187DFF1A9F"
	},
	{
	    "interface": "MAC4",
	    "macaddr": "00187DFF1AA0"
	},
	{
	    "interface": "MAC5",
	    "macaddr": "00187DFF1AA1"
	},
	{
	    "interface": "MAC6",
	    "macaddr": "00187DFF1AA2"
	}
    ],
    "operationInfo": {
    "WriteIMAGE": "",
    "WriteMAC": "",
    "VerifyMAC": "",
	"WriteVPD": "",
	"MESBURNSTART": "",
	"MESHWTEST": "",
	"MESBURNTEST": "",
	"MESPOSTTEST": "",
	"CLEARDEVICE": ""
    },
    "testInfo": {},
    "hwtestInfo": [],
    "burntestInfo":[],
    "lasttestInfo":[],
    "performancestatsInfo": [
        {
	    "nic": "enp2s0f1",
	    "average": 932,
	    "min": 910,
	    "max": 937
	},
	{
	    "nic": "enp3s0f0",
	    "average": 933,
	    "min": 913,
	    "max": 937
	},
	{
	    "nic": "enp3s0f1",
	    "average": 931,
	    "min": 909,
	    "max": 936
	},
	{
	    "nic": "enp2s0f0",
	    "average": 930,
	    "min": 905,
	    "max": 936
	},
	{
	    "nic": "enp1s0f1",
	    "average": 930,
	    "min": 909,
	    "max": 936
	}
    ]
}

```

###Response
Success:
```
{"msg" : "PDF successfully rendered"}
```
Error:
```
{"msg" : exception}
```

## pdf will be generated in "/home/test/reports" with name: [Device Serial number]_TestReport.pdf

#### git clone repository
#### run --> ./reportGenerator_setup.sh
#### then run --> systemctl start reportGenerator.service


