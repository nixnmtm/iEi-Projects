# Scan BurnIn devices

## Device Side:

1. Start scanning when command received in all client devices.

    ``` Fanout mechanism    - exchange = 'devicescan'
                            - exchange_type = fanout
                            - queue --> exlcusive = True
             should be maintained in both Producer and Consumer ```
            
2. Locally, retrieve the pci information from /device_client/utils/hwinfo.py.
3. Publish it back to edge server using the same connection through unique route key.

       ``` Work Queue mechanism - queue_name = 'hwinfo_queue'
                                - durable = True ```

## Server Side:

5. GET MES data from device_info API and compare with local pci data.
6. POST compared response/log to deviceScan log API.
7. If any internal error or complete success, POST it to notifications API.
8. Check if all macs passed the scan, then the device result is "Pass" and send to Pair API.

#### To clone single branch:
git clone -b PuzzleScanDev --single-branch http://40.74.91.221/puzzle/device-intel-factory.git Puzzle_Scanning

#### ---------------------------------------------------------------------------------------------------------

### **Dependencies:**

* Python 3.5
* flask 1.0.2
* pika 0.11.0
* requests 2.19.1
* more_itertools 4.2.0

##### RabbitMQ Version: 3.7.7(Erlang 21.0)

**Note:** Refer cmds.md for service related commands

#### Format of Scanning log send to deviceScan log API
1. "scanstatus" : (0:Fail, 1: Pass) # for each MAC in a device
2. "result": (0:Fail, 1: Pass) # if all macs passed the scan, then result is "Pass" and send to Pair API


```
{
    "operationid": 1,
    "pairInfo": [],
    "scaninfo": [
        {
            "macinfo": [
                {
                    "interface": "enp4s0",
                    "macaddr": "e0:18:7d:2e:ca:68",
                    "scanstatus": "1"
                },
                {
                    "interface": "enp6s0",
                    "macaddr": "e0:18:7d:2e:ca:6a",
                    "scanstatus": "0"
                },
                {
                    "interface": "enp5s0",
                    "macaddr": "e0:18:7d:2e:ca:69",
                    "scanstatus": "0"
                }
            ],
            "sn": Q186I15901,
            "result": "0"
        },
        {
            "macinfo": [
                {
                    "interface": "enp5s0",
                    "macaddr": "e0:18:7d:2e:ca:69",
                    "scanstatus": "1"
                },
                {
                    "interface": "enp2s0f3",
                    "macaddr": "00:18:7d:a4:cc:a6",
                    "scanstatus": "1"
                },
                {
                    "interface": "enp8s0",
                    "macaddr": "e0:18:7d:2e:cb:44",
                    "scanstatus": "1"
                }
            ],
            "sn": Q186I15815,
            "result": "1"
        }
    ]
}

```

#### Format of notification send to Notification API

```
{
    "operationId" : "shgbshjhdstiuy978677",
    "scanInfo" :[
                  {"serialNo": "V123821038SDF",
                  "result"  : "Success"},
                  {"serialNo": "Q186I15815",
                  "result"  : "Success"},
                  {"serialNo": "Q186I15801",
                  "result"  : "Fail"}
                ]
}
```


#### Format of notification to Pair API

```
{
"snArray" : ["Q186I15815", "V123821038SDF"],
"operationId": "shgbshjhdstiuy978677"
}

```

#### Format of notification to directBurn API

```
{
"snArray" : ["Q186I15815", "V123821038SDF"],
"operationId": "shgbshjhdstiuy978677"
"operatorId" : "llkj0001"
"scanMode" : 1
}

```

### Covert script to executable binary

1. pip3 install pyinstaller 

2. pyinstaller -F --paths \<your main python script path\> --paths \<importing functions path\>  \<python program.py\>
    
    In --paths flags include the path of importing custom functions and main program
    
    **Example:** 
    > pyinstaller -F --paths ./device_client/ --paths ./device_client/utils/  ./device_client/device_scan.py

3. Two folders named, build and dist will be created, where, binary executable will in the dist folder.

### Compress the project into tar

create setup.py manually and then

> python setup.py sdist