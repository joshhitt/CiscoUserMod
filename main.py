#!/usr/local/bin/python3.9
# Cisco Account Automation
# This is basic function that will log into a switch and add or change a user account and password.

import datetime
import os
import re
# import threading
import time
from getpass import getpass
import paramiko

print('\n    #### Caution Updating all IOS Devices enter \'Cntrl\' \'C\' to Exit ####\n\n')
sshUsername = input(" Enter User Name: ").strip()
sshPassword = getpass(" Enter Current Password: ").strip()
newUser = input(" Enter the User account to add or change: ").strip()
while True:
    try:
        privLevel = int(input(" Enter Privilege Level: "))
        assert 0 < privLevel < 16
    except ValueError:
        print(" Use a number between 1 - 15\n")
    except AssertionError:
        print(" Use a number between 1 - 15\n")
    else:
        break

while True:
    newPass = getpass(" Enter your new Password: ").strip()
    # if(len(newPass)>=8):
    if not bool(re.match(r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*/?]).{8,30})', newPass)):
        print("    You have entered an invalid password.\n")
    else:
        break  # moving on


# noinspection PyPep8Naming
class ssh:
    shell = None
    client = None
    transport = None

    def __init__(self, ipaddr, user, passwd):
        print("Connecting to host: ", str(ipaddr))
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(ipaddr, username=user, password=passwd, look_for_keys=False)
        self.transport = paramiko.Transport((ipaddr, 22))
        self.transport.connect(username=user, password=passwd)

    def close_connection(self):
        if self.client is not None:
            self.client.close()
            self.transport.close()

    def open_shell(self):
        self.shell = self.client.invoke_shell()

    def send_shell(self, command):
        if self.shell:
            self.shell.send(command + "\n")
        else:
            print("Connection Failed.")

time_now = datetime.datetime.now().strftime('%H:%M:%S %m/%d/%Y')
infilepath = os.path.expanduser('~/scripts/')  # UNIX Pathing
devicelist = "custom_devices.txt"  # Set devicelist default
# devicelist = "ios_devices.txt"  # Set devicelist default
input_file = open(infilepath + devicelist, "r")
print(f"\n   Using File Path {infilepath} {devicelist}\n")  # debug line verifying the device list
iplist = input_file.readlines()
input_file.close()
try:
    for ip in iplist:
        time.sleep(1)
        try:
            host = ip.strip()
            connection = ssh(host, sshUsername, sshPassword)
            connection.open_shell()
            connection.send_shell('conf term')  # Cmd1
            connection.send_shell(f'username {newUser} privilege {privLevel} secret 0 {newPass}')  # Cmd2
            connection.send_shell('end')  # Cmd3
            connection.send_shell('write mem')  # Cmd4
            time.sleep(2)
            connection.send_shell('exit')  # Cmd5 
            time.sleep(1)
            print('\n')
            connection.close_connection()
        finally:
            pass
finally:
    print(f"\n    Devices Updated: {time_now}")
