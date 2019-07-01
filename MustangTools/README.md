## Discover devices connected with server

# API 1 (Discover API):
> http://localhost:3332/mustangTools/discover

### Method: GET
Response: 
```
{
    "ip": ["192.168.0.117"]
}
```
### Method: POST

Query:
```
"serverIP" : "10.10.70.114"
```

Response:
```
{
    "ip": ["10.10.70.26"]
}
```

# API 2 (MustangV100 burn API):

> http://localhost:3332/mustangTools/mustangBurn

### Method: POST
No body

Response:
```
{
"snArray": ["MX987HGTY", "MXF65478J"], "infoSN": "MQTClJN"}
}
```

if no data fetched:
```
{
    "infoSN": "",
    "snArray": ""
}
```

#### Notification response
```
{
"ip": "10.10.70.129", "sn": "MX987HGTY", 
"snArray": ["SNCARD001IUH", "SNCARD00198JV"]
}

```



# API 3 (MustangV100 Test API):

> http://localhost:3332/mustangTools/mustangTest

### Method: GET

Response:
```
{
"info": [
{
"ip" : "10.10.70.62",
"sn" : "MX987HGTY",
"snArray" : ["MQTClJN", "MQTClJGH", "UTFYTF"]
},
{
"ip" : "10.10.70.26",
"sn" : "MXF65478J",
"snArray" : ["MQTDRDJN", "FDTDRYU"]
}
       ]
```
if No data fetched:
```
{ 
"info": "No data accumulated from scanmustang. Hint: May be all in Test stage"
}
```
if Error:
```
{
"info" : "mustangDevs: List index out of range"
}
```

# API 4 (MustangV100 Digits API):

> http://localhost:3332/mustangTools/mustangDigits

### Method: GET

Response:

```
"info": [
  {
	"ip" : "10.10.70.62",
	"digits" : ["0","1"]
  },
  {
	"ip" : "10.10.70.131",
	"digits" : ["0","1"]
  },
  {
	"ip" : "10.10.70.26",
	"digits" : ["0","1"]
  }
]
```



