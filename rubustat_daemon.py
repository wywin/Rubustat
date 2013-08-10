#! /usr/bin/python
 
import sys
import subprocess
import os
import time
import RPi.GPIO as GPIO
import datetime
import sqlite3

from daemon import Daemon
from getIndoorTemp import getIndoorTemp

###Begin helper functions###



class rubustatDaemon(Daemon):
    
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
        #delay to preserve processor
        time.sleep(360)
        return 0

    def run(self):
        lastLog = datetime.datetime.now()
        while True:

            indoor_temp = float(getIndoorTemp())
            hvac_state = int(getHVACState())

            file = open("/home/pi/src/Rubustat/status", "r")
            set_temp = float(file.readline())
            mode = file.readline()
            file.close()

            now = datetime.datetime.now()
            logElapsed = now - lastLog
            if logElapsed > datetime.timedelta(minutes=6):
                c.execute('INSERT INTO logging VALUES(?, ?, ?)', (now, indoor_temp, set_temp))
                conn.commit()
                lastLog = datetime.datetime.now()
            # heater mode
            if mode == "heat":
                if hvac_state == 0: #idle
                    if indoor_temp < set_temp - inactive_hysteresis:
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to heat at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = heat()

                elif hvac_state == 1: #heating
                    if indoor_temp > set_temp + active_hysteresis:
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        fan_to_idle()
                        time.sleep(30)
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = idle()

                elif hvac_state == -1: # it's cold out, why is the AC running?
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = idle()

            # ac mode
            elif mode == "cool":
                if hvac_state == 0: #idle
                    if indoor_temp > set_temp + inactive_hysteresis:
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to cool at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = cool()

                elif hvac_state == -1: #cooling
                    if indoor_temp < set_temp - active_hysteresis:
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        fan_to_idle()
                        time.sleep(30)
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = idle()

                elif hvac_state == 1: # it's hot out, why is the heater on?
                        if DEBUG == 1:
                            log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvac_state = idle()
            else:
                print "It broke."

            #DEBUG stuff
            if DEBUG == 1:
                heatStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value").read().strip())
                coolStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value").read().strip())
                fanStatus = int(os.popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value").read().strip())
                log = open("/home/pi/src/Rubustat/logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                log.write("Report at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ":\n")
                log.write("hvac_state = " + str(hvac_state)+ "\n")
                log.write("indoor_temp = " + str(indoor_temp)+ "\n")
                log.write("set_temp = " + str(set_temp)+ "\n")
                log.write("heatStatus = " + str(heatStatus) + "\n")
                log.write("coolStatus = " + str(coolStatus)+ "\n")
                log.write("fanStatus = " + str(fanStatus)+ "\n")
                log.close()
            
            time.sleep(5)


if __name__ == "__main__":
        daemon = rubustatDaemon('/tmp/rubustatDaemon.pid')

        DEBUG = 1

        active_hysteresis = 0.0
        inactive_hysteresis = 0.5

        #GPIO pins, reassign these for your hardware configuration!!!
        HEATER_PIN = 24
        AC_PIN = 23
        FAN_PIN = 25

        #NOTE: thermometer is read via Dallas 1-wire, as per 
        #http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
        #<3 to adafruit


        #There is probably a better way to set this up,
        #than running the exports and making directories every time
        #but it works for now...

        #Setting up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HEATER_PIN, GPIO.OUT)
        GPIO.setup(AC_PIN, GPIO.OUT)
        GPIO.setup(FAN_PIN, GPIO.OUT)
        os.popen("echo " + str(HEATER_PIN) + " > /sys/class/gpio/export")
        os.popen("echo " + str(AC_PIN) + " > /sys/class/gpio/export")
        os.popen("echo " + str(FAN_PIN) + " > /sys/class/gpio/export")
        #Setting up logs
        os.popen("mkdir /home/pi/src/Rubustat/logs")

        conn = sqlite3.connect("/home/pi/src/Rubustat/tempLogs.db")
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS logging (datetime TIMESTAMP, actualTemp FLOAT, targetTemp INT)')    

        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)