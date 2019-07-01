import queue
import more_itertools as mit
import logging


class BurnScheduler(object):

    """ Scheduling Burn Task based on the device availability
    integers mapped for
    0 - wifi
    1 - ram
    2 - lan
    """
    def __init__(self, devs, status_handle):

        # GLOBAL variables
        self.devs = devs
        self.status_handle = status_handle
        # append the status_handle with new devices dynamically

        if not status_handle:
            if len(devs) > 0:
                for m in devs:
                    dev_status = dict()
                    dev_status["sn"] = m
                    dev_status["run_state"] = None
                    dev_status["completed"] = []
                    self.status_handle.append(dev_status)
            else:
                logging.error("No devices provided")
        self.wifi_q = queue.Queue()

    @staticmethod
    def split_list(a_list):
        half = len(a_list)//2
        return a_list[:half], a_list[half:]

    def init_allocate_task(self, dev_list):
        half1, half2 = self.split_list(dev_list)
        firstdev = half1.pop(0)
        if self.check_runstate(firstdev) is None:
            self.wifi_q.put(firstdev)
        else:
            logging.info("{} is busy with other tasks".format(firstdev))
        for d1 in half1:
            if self.check_runstate(d1) is None:
                self.ram_burn(d1)
        for d2 in half2:
            if self.check_runstate(d2) is None:
                self.lan_burn(d2)
        return "Burn initialized for {} devices".format(len(dev_list))

    def check_runstate(self, dev):
        """
        Checks and returns the device run state.
        dev -- device serial number (string)
        return --   None
               --   wifi = 0
               --   ram = 1
               --   lan = 2
        """
        ndx = list(mit.locate(self.status_handle, pred=lambda d: d["sn"] == dev))[0]
        if self.status_handle[ndx]["run_state"] is None:  # if run_state is empty
            return None  # slot is free, nothing running
        elif self.status_handle[ndx]["run_state"] == 0:  # in wifi burn
            return 0
        elif self.status_handle[ndx]["run_state"] == 1:  # in ram burn
            return 1
        elif self.status_handle[ndx]["run_state"] == 2:
            return 2 # in lan burn

    def update_run_status(self, dev, task=None):
        """
        Checks and updates the device run state.
        dev -- device serial number (string)
        return --   None
               --   wifi = 0
               --   ram = 1
               --   lan = 2
        """
        index = list(mit.locate(self.status_handle, pred=lambda d: d["sn"] == dev))[0]
        if task == "wifi":
            self.status_handle[index]["run_state"] = 0
        elif task == "ram":
            self.status_handle[index]["run_state"] = 1
        elif task == "lan":
            self.status_handle[index]["run_state"] = 2
        return self.status_handle

    def clear_run_state(self, dev):
        index = list(mit.locate(self.status_handle, pred=lambda d: d["sn"] == dev))[0]
        self.status_handle[index]["run_state"] = None

    def check_completed_dev(self, dev):
        ndx = list(mit.locate(self.status_handle, pred=lambda d: d["sn"] == dev))[0]
        if self.status_handle[ndx]["completed"] is None:  # if run_state is empty
            return None  # slot is free, nothing completed
        else:
            return self.status_handle[ndx]["completed"]
        # elif 0 in self.status_handle[ndx]["completed"]:
        #     return 0  # wifi burn completed
        # elif 1 in self.status_handle[ndx]["completed"]:
        #     return 1  # ram burn completed
        # elif 2 in self.status_handle[ndx]["completed"]:
        #     return 2  # lan burn completed

    def update_completed_dev(self, dev, task=None):
        index = list(mit.locate(self.status_handle, pred=lambda d: d["sn"] == dev))[0]
        if task == "wifi":
            self.status_handle[index]["completed"].append(0)
        if task == "ram":
            self.status_handle[index]["completed"].append(1)
        if task == "lan":
            self.status_handle[index]["completed"].append(2)
        return self.status_handle

    def burning_devs(self, task):
        """Check the current run status of devices and return devices list in each burn task
        Note: wifi running should have only one device running.
        task -- wifi or ram or lan (string)
        return -- list of devices for given task
        """
        wifi_running = []
        ram_running = []
        lan_running = []
        for i in self.status_handle:
            if self.check_runstate(i["sn"]) == 0:
                wifi_running.append(i["sn"])
            elif self.check_runstate(i["sn"]) == 1:
                ram_running.append(i["sn"])
            elif self.check_runstate(i["sn"]) == 2:
                lan_running.append(i["sn"])
        if task == "wifi":
            return wifi_running
        if task == "ram":
            return ram_running
        if task == "lan":
            return lan_running

    def wifi_burn(self):
        if not self.wifi_q.empty():  # if wifi queue is not empty
            if self.check_runstate(self.wifi_q.queue[0]) is None: # if peeked element runstate is None
                self.update_run_status(self.wifi_q.queue[0], task="wifi")
                print("Call Wifi API", self.wifi_q.queue[0])
        else:
            return "wifi queue is empty"

    def ram_burn(self, dev):
        self.update_run_status(dev, task="ram")
        print("Call RAM API", dev)

    def lan_burn(self, dev):
        self.update_run_status(dev, task="lan")
        print("Run LAN API", dev)

    def pause_lan(self, dev):
        # call pause api # pause lan burn and send device to wifi
        self.clear_run_state(dev)

    def run(self, init=False):
        if init is True:
            self.init_allocate_task(self.devs)
        else:
            dev2burn = self.devs[0] # if triggered for a single device
            run_status = self.check_runstate(dev2burn)
            # call API to know completed status  #### API CALL
            self.update_completed_dev(dev2burn, task="") # update the status of the device based on task
            completed_status = self.check_completed_dev(dev2burn)
            if run_status == 0: # if device run_state in wifi
                if 0 in completed_status: # If already completed
                    self.clear_run_state(dev2burn) # clear the run state
                    if self.wifi_q.queue[0] == dev2burn:
                        self.wifi_q.get()  # deque the device which is completed
                        self.wifi_burn()  # trigger the next element for wifi burn
                    else:
                        logging.error("FIFO device and WIFI burn completed device does not match")
                else:
                    logging.error("Triggered before completion of wifi burn")
            elif run_status == 1:
                if 1 in completed_status:
                    self.clear_run_state(dev2burn)
                else:
                    logging.error("Triggered before completion of ram burn")
            elif run_status == 2:
                if 2 in completed_status:
                    self.clear_run_state(dev2burn)
                else:
                    logging.error("Triggered before completion of lan burn")
            run_status =  self.check_runstate(dev2burn) # check now the run_state, should be None
            if run_status is None:  # device not in any burn state
                if 0 not in completed_status:
                    self.wifi_q.put(dev2burn)
                elif 1 not in completed_status:
                    self.ram_burn(dev2burn)
                elif 2 not in completed_status:
                    self.lan_burn(dev2burn)
                else:
                    logging.info("All Burn Done for device {}".format(dev2burn))

            if 0 not in completed_status:
                if self.wifi_q.qsize() == 0 and run_status == 2: # nothing in queue, but lan is running
                    self.pause_lan(dev2burn)
                    self.wifi_q.put(dev2burn)
                    self.wifi_burn()

        # update database with updated sta
        dbAPI = True
        if dbAPI:
            print
            #  update the current modifications
        return

# ***** Think how to initiate this
# if __name__ == '__main__':
#     # get status from database
#     dbAPI = dict()  # for time being
#     if dbAPI:
#         # populate from db
#         # status_handle = from db
#         pass
#     else:
#         status_handle = []
#
#     #Get scanned devices list
#
#     trigger_api = dict()
#     scanned_devs = trigger_api["snArray"] # get discovered devices from API
#
#     # Get trigger response after a task is done for a device
#     trigger_api = dict()
#     dev_sn = trigger_api["sn"]
#
#     #Check and decide initial or normal Task allocation
#     if isinstance(scanned_devs, list): # check passed is a list
#         BS = BurnScheduler(scanned_devs, status_handle) # instatiate class object with scanned devices from discover API
#         # check if all run_status is None and completed status is None
#         check_empty = [True for i in status_handle if i["run_state"] is None and i["completed"] is not None]
#         if scanned_devs:
#             if all(check_empty):  # if all True(meaning all states are None), then enter statement
#                 logging.info("Running {}".format(BS.init_allocate_task.__name__))
#                 BS.run(init=True)
#             else:
#                 if len(scanned_devs) > 1:
#                     logging.info("Running {}".format(BS.init_allocate_task.__name__))
#                     BS.run(init=True)
#                 else:
#                     BS.run()
#         else:
#             logging.error("No device passes from dicover API")