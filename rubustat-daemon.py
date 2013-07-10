#! /usr/bin/python
 
import sys
import subprocess
import os
import time

active_hysteresis = 0.0
inactive_hysteresis = 0.5
outdoor_temp_buffer = 5

DEBUG = 0

#infinite loop is the same as a daemon, right?
while 1 == 1:


    indoor_temp = float(subprocess.check_output("./etc.sh indoor_temp"))
    outdoor_temp = float(subprocess.check_output("./etc.sh outdoor_temp"))
    hvac_state = int(subprocess.check_output("./etc.sh get_state"))

    file = open("set_temp", "r")
    set_temp = float(file.readline())
    file.close()
     
    # heater mode
    if outdoor_temp < set_temp:
        if hvac_state == 0: #idle
            if indoor_temp < set_temp - inactive_hysteresis:
                os.system("./etc.sh heat")
                hvac_state = 1
        elif hvac_state == 1: #heating
            if indoor_temp > set_temp + active_hysteresis:
                os.system("./etc.sh fan_to_idle") 
                time.sleep(300)
                os.system("./etc.sh idle")
                hvac_state = 0
        elif hvac_state == -1: # it's cold out, why is the AC running?
                os.system("./etc.sh idle")
    # ac mode
    else:
        if hvac_state == 0: #idle
            if indoor_temp > set_temp + inactive_hysteresis:
                os.system("./etc.sh cool")
                hvac_state = -1
        elif hvac_state == -1: #cooling
            if indoor_temp < set_temp - active_hysteresis:
                os.system("./etc.sh fan_to_idle") 
                time.sleep(300)
                os.system("./etc.sh idle")
                hvac_state = 0
        elif hvac_state == 1: # it's hot out, why is the heater on?
                os.system("./etc.sh idle")

    #debug stuff
    if DEBUG == 1:
        print "Sleepy time!"
        print "hvac_state = " + str(hvac_state)
        print "indoor_temp = " + str(indoor_temp)
        print "outdoor_temp = " + str(outdoor_temp)
        print "set_temp = " + str(set_temp)

    time.sleep(10)