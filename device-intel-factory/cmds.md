#### DScanning Client as Service:

1. Run setup_dScanning.sh
2. START    : ```systemctl start dScanning.service```
3. ENABLE   : ```systemctl enable dScanning.service``` ---> to make it run even after reboot
4. RESTART  : ```systemctl restart dScanning.service```
5. STATUS   : ```systemctl status dScanning.service```
6. STOP     : ```systemctl stop dScanning.service```
7. ACTIVE or NOT : ```systemctl is-active dScanning.service```
8. ENABLED or NOT : ```systemctl is-enabled dScanning.service```

#### SSCanning Server as Service:

1. Run setup_sScanning.sh
2. START  : ```systemctl start sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
3. ENABLE : ```systemctl enable sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
4. RESTART : ```systemctl restart sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
5. STATUS : ```systemctl status sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
6. STOP   : ```systemctl stop sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
7. ACTIVE or NOT : ```systemctl is-active sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```
8. ENABLED or NOT : ```systemctl is-enabled sScanning@"localhost 5672 rmquser 123456 localhost 3000 3000"```


