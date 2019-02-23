import threading
import time

import ball
import tape3
import thread_example
from networktables import NetworkTables as nt

ip = "10.15.12.2"

nt.initialize(server=ip)
table = nt.getTable("chooser_data")

sem = threading.BoundedSemaphore(value=1)
stop_message = [0]

def start_tape():
    tape3.main(stop_message, sem)

def start_ball():
    ball.main(stop_message, sem)

def start_example():
    thread_example.main(stop_message, sem)

#Listens to networktable, runs when a value is changed
def valueChanged(table, key, value, isNew):
    print("Value changed:", table, key, value)
    # 0 stops everything
    # 1 stops everything but tape detector
    # 2 stops everything but ball detector
    value = int(value)
    stop_message[0] = value
    
    if value != 0: 

        t = threading.Thread(target=target_list[value])
        sem.acquire() #Decrements semaphore value, waits for other scripts to stop

        print("[*]Starting thread: {}".format(value))
        t.start() #Starts thread

#Watches the connection to the networktables server
def connectionListener(info, connected):
    print(info, "Connected:", connected)

target_list=[0, start_tape, start_ball, start_example]

nt.addConnectionListener(connectionListener)

table.addEntryListener(valueChanged)

while True:
    time.sleep(5)
