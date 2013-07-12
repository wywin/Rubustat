#! /usr/bin/python
 
import sys
import subprocess
import os
import time

import RPi.GPIO as GPIO

DEBUG = 0

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

def getOutdoorTemp():
    outdoor_temp=os.popen("curl -s -m 20 http://rss.accuweather.com/rss/liveweather_rss.asp\?metric\=" + METRIC + "\&locCode\=" + ZIP + "| grep -i -m1 'currently' | grep -o '\-\?[0-9]\+'").read().strip()
    return outdoor_temp

def getIndoorTemp():
    #TODO: implement when hardware arrives
    return 70

def getHVACState():
    heatStatus = os.popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value").read().strip()
    coolStatus = os.popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value").read().strip()
    fanStatus = os.popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value").read().strip()
    
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
    outdoor_temp = float(getOutdoorTemp())
    hvac_state = int(getHVACState())

    file = open("set_temp", "r")
    set_temp = float(file.readline())
    file.close()
     
    # heater mode
    if outdoor_temp < set_temp:
        if hvac_state == 0: #idle
            if indoor_temp < set_temp - inactive_hysteresis:
                hvac_state = heat()
        elif hvac_state == 1: #heating
            if indoor_temp > set_temp + active_hysteresis:
                fan_to_idle()
                time.sleep(300)
                hvac_state = idle()
        elif hvac_state == -1: # it's cold out, why is the AC running?
                hvac_state = idle()
    # ac mode
    else:
        if hvac_state == 0: #idle
            if indoor_temp > set_temp + inactive_hysteresis:
                hvac_state = cool()
        elif hvac_state == -1: #cooling
            if indoor_temp < set_temp - active_hysteresis:
                fan_to_idle()
                time.sleep(300)
                hvac_state = idle()
        elif hvac_state == 1: # it's hot out, why is the heater on?
                hvac_state = idle()

    #debug stuff
    if DEBUG == 1:
        print "Sleepy time!"
        print "hvac_state = " + str(hvac_state)
        print "indoor_temp = " + str(indoor_temp)
        print "outdoor_temp = " + str(outdoor_temp)
        print "set_temp = " + str(set_temp)

    time.sleep(10)