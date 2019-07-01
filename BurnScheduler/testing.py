def check(dev):
    return 2

print(check("jj"))
if check("de") == 2:
    print("HI")


hi = {"hello":None}
hi["hello"] = 0
print(hi)

import queue

status_handle = []
devs = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]

# wifi_q = queue.Queue()
# wifi_q.put(devs[0])
# wifi_q.put(devs[1])
# wifi_q.put(devs[2])
# wifi_q.put(devs[3])
# wifi_q.put(devs[4])
# wifi_q.put(devs[5])
#
# print("init", wifi_q.queue)
# print("1st", wifi_q.queue[0])
# wifi_q.get()
# print("After deque",wifi_q.queue)
# print("qsize:", wifi_q.qsize())
#
# print("init", wifi_q.queue)
# print("2nd", wifi_q.queue[0])
# wifi_q.get()
# print("After deque", wifi_q.queue)
# print("qsize:", wifi_q.qsize())
#
# jjj = [ True for i in status_handle if i["run_state"] is None and i["completed"] is not None]
# if all(jjj):
#     print("jjjjj", True)
#
# print("HIHIHI", jjj)

from burnScheduler import TaskScheduler
TS = TaskScheduler(devs=devs, status_handle=status_handle)
print(TS.status_handle)
TS.wifi_q.put("D1")
TS.wifi_burn()



def burning_devs(task):
    """Check the current run status of devices and return devices in wifi burn
    Note: wifi running should have only one device running.
    """
    wifi_running = []
    ram_running = []
    lan_running = []
    for i in status_handle:
        if TS.check_runstate(i["sn"]) == 0:
            wifi_running.append(i["sn"])
        elif TS.check_runstate(i["sn"]) == 1:
            ram_running.append(i["sn"])
        elif TS.check_runstate(i["sn"]) == 2:
            lan_running.append(i["sn"])
    if task == "wifi":
        return wifi_running
    if task == "ram":
        return ram_running
    if task == "lan":
        return lan_running


print("WIFI", burning_devs("wifi"))
print("RAM", burning_devs("ram"))
print("LAN", burning_devs("lan"))