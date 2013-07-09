#! /usr/bin/python
 
import sys
import subprocess
import os
import time

active_hysteresis = 0.0
inactive_hysteresis = 0.5
outdoor_temp_buffer = 5
os.chdir(os.getcwd())
while 1 == 1:


    indoor_temp = float(subprocess.check_output("./get_indoor_temp.sh"))
    outdoor_temp = float(subprocess.check_output("./get_outdoor_temp.sh"))

    file = open("set_temp", "r")
    set_temp = float(file.readline())
    file.close()
     
    hvac_state = int(subprocess.check_output("./get_hvac_state.sh"))
    
    # heater mode
    if outdoor_temp < set_temp:
        if hvac_state == 0: #idle
            if indoor_temp < set_temp - inactive_hysteresis:
                os.system("./hvac_heat.sh")
                hvac_state = 1
        elif hvac_state == 1: #heating
            if indoor_temp > set_temp + active_hysteresis:
                os.system("./hvac_idle.sh")
        elif hvac_state == -1: # it's cold out, why is the AC running?
                os.system("./hvac_idle.sh")
    # ac mode
    else:
        if hvac_state == 0: #idle
            if indoor_temp > set_temp + inactive_hysteresis:
                os.system("./hvac_cool.sh")
                hvac_state = -1
        elif hvac_state == -1: #cooling
            if indoor_temp < set_temp - active_hysteresis:
                os.system("./hvac_idle.sh")
                hvac_state = 0
        elif hvac_state == 1: # it's hot out, why is the heater on?
                os.system("./hvac_idle.sh")

    #debug stuff
    print "Sleepy time!"
    print "hvac_state = " + str(hvac_state)
    print "indoor_temp = " + str(indoor_temp)
    print "outdoor_temp = " + str(outdoor_temp)
    print "set_temp = " + str(set_temp)
    time.sleep(10)