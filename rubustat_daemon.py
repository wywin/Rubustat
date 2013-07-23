#! /usr/bin/python
 
import sys
import subprocess
import os
import time
from getIndoorTemp import getIndoorTemp
import RPi.GPIO as GPIO


DEBUG = 1

METRIC=0 # 0 for F, 1 for C
ZIP=37216
active_hysteresis = 0.0
inactive_hysteresis = 0.5
outdoor_temp_buffer = 5

#GPIO pins
HEATER_PIN = 23
AC_PIN = 24
FAN_PIN = 25

#NOTE: thermometer will be read via Dallas 1-wire, as per 
#http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

#Setting up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(HEATER_PIN, GPIO.OUT)
GPIO.setup(AC_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

###Begin helper functions###

def getHVACState():
    heatStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value").read().strip())
    coolStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value").read().strip())
    fanStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value").read().strip())
    if heatStatus == 1 and fanStatus == 1:
        #heating
        return 1
    elif coolStatus == 1 and fanStatus == 1:
        #cooling
        return -1
    elif heatStatus == 0 and coolStatus == 0 and fanStatus == 0:
        #idle
        return 0
    else:
        #broken
        return 2

def cool():
    GPIO.output(HEATER_PIN, False)
    GPIO.output(AC_PIN, True)
    GPIO.output(FAN_PIN, True)
    return -1

def heat():
    GPIO.output(HEATER_PIN, True)
    GPIO.output(AC_PIN, False)
    GPIO.output(FAN_PIN, True)
    return 1

def fan_to_idle(): 
    #to blow the rest of the heated / cooled air out of the system
    GPIO.output(HEATER_PIN, False)
    GPIO.output(AC_PIN, False)
    GPIO.output(FAN_PIN, True)

def idle():
    GPIO.output(HEATER_PIN, False)
    GPIO.output(AC_PIN, False)
    GPIO.output(FAN_PIN, False)
    return 0

###begin main loop###
#infinite loop is the same as a daemon, right?
while 1 == 1:

    indoor_temp = float(getIndoorTemp())
    hvac_state = int(getHVACState())

    file = open("status", "r")
    set_temp = float(file.readline())
    mode = file.readline()
    file.close()
     
    # heater mode
    if mode == "heat":
        if hvac_state == 0: #idle
            if indoor_temp < set_temp - inactive_hysteresis:
                hvac_state = heat()
        elif hvac_state == 1: #heating
            if indoor_temp > set_temp + active_hysteresis:
                fan_to_idle()
                time.sleep(30)
                hvac_state = idle()
        elif hvac_state == -1: # it's cold out, why is the AC running?
                hvac_state = idle()
    # ac mode
    elif mode == "cool":
        if hvac_state == 0: #idle
            if indoor_temp > set_temp + inactive_hysteresis:
                hvac_state = cool()
        elif hvac_state == -1: #cooling
            if indoor_temp < set_temp - active_hysteresis:
                fan_to_idle()
                time.sleep(30)
                hvac_state = idle()
        elif hvac_state == 1: # it's hot out, why is the heater on?
                hvac_state = idle()
    else:
        print "It broke."

    #debug stuff
    if DEBUG == 1:
        print "Sleepy time!"
        print "hvac_state = " + str(hvac_state)
        print "indoor_temp = " + str(indoor_temp)
        print "set_temp = " + str(set_temp)
        log = open("debug.log", "a")
        log.write("Sleepy time!")
        log.write("hvac_state = " + str(hvac_state))
        log.write("indoor_temp = " + str(indoor_temp))
        log.write("set_temp = " + str(set_temp))
        log.close()
    time.sleep(10)
