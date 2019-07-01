# App Centre
#### Managing Apps (Install, Uninstall)   
```
sudo apt install python3-pip   
pip3 install flask_cors 
swapoff -a
```

Available Apps:
1. OVS
2. Docker
3. Kubernetes
4. QEMU_KVM


### Install

POST:

URL: http://localhost:8200/appcentre/install

Input : 
```
{
  "app_name": "kubernetes"
}
```

Response:
```
{
    "msg": "kubernetes is successfully installed",
    "status": 1 (success)
}
                or
{
    "msg": "kubernetes is already installed"
    "status": 1 (success)
}
                or
{
    "msg": "catched error"
    "status": 0 (fail)
}
```

### Uninstall

POST:

URL: http://localhost:8200/appcentre/uninstall

Body : {"app_name": "docker"}

Response:

```
{
    "msg": "docker is successfully uninstalled",
    "status": 1 (success)
}
                or
{
    "msg": "docker module not found. Cannot uninstall"
    "status": 1 (success)
}

{
    "msg": "catched error"
    "status": 0 (fail)
}

```

### Installed App Status

GET:

URL: http://10.10.70.16:8200/appcentre/apps_status

Response:
```
{
    "apps": [
        {
            "app_name": "ovs",
            "status": "Not Installed",
            "version": "2.6.1"
        },
        {
            "app_name": "kubernetes",
            "status": "Installed",
            "version": "v1.11.3"
            "url": "http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/"
        },
        {
            "app_name": "docker",
            "status": "Not Installed",
            "version": "17.05.0-ce"
        },
         {
            "app_name": "qemu_kvm",
            "status": "Not Installed"
        }
    ]
}

```

### App Dependency

POST:

URL: http://localhost:8200/appcentre/app_limit

```
Body : {
        "app_name": "kubernetes",
        "action": "install/uninstall"
        }
```

Response:
```
{
 "app_name": "kubernetes",
 "dependency": True/False(boolean),
 "msg": "Kubernetes is dependent on Docker. Do you wish to proceed installing docker?"
 
}

```

### Launch Kubernetes UI

GET:

URL: http://10.10.70.16:8200/appcentre/kube_launch

### Kubernetes Dashboard UI   

http://10.10.70.92:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/  

