#! /usr/bin/python
 
import sys
import subprocess
import os
import time
import RPi.GPIO as GPIO
import datetime
import ConfigParser

from daemon import Daemon
from getIndoorTemp import getIndoorTemp

#set working directory to where "rubustat_daemon.py" is
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#read values from the config file
config = ConfigParser.ConfigParser()
config.read("config.txt")
DEBUG = int(config.get('main','DEBUG'))
active_hysteresis = float(config.get('main','active_hysteresis'))
inactive_hysteresis = float(config.get('main','inactive_hysteresis'))
HEATER_PIN = int(config.get('main','HEATER_PIN'))
AC_PIN = int(config.get('main','AC_PIN'))
FAN_PIN = int(config.get('main','FAN_PIN'))

sqliteEnabled = config.getboolean('sqlite','enabled')
if sqliteEnabled == True:
    import sqlite3

#mail config
mailEnabled = config.getboolean('mail', 'enabled')
if mailEnabled == True:
    import smtplib

    config.read("mailconf.txt")
    SMTP_SERVER = config.get('mailconf','SMTP_SERVER')
    SMTP_PORT = int(config.get('mailconf','SMTP_PORT'))
    username = config.get('mailconf','username')
    password = config.get('mailconf','password')
    sender = config.get('mailconf','sender')
    recipient = config.get('mailconf','recipient')
    subject = config.get('mailconf','subject')
    body = config.get('mailconf','body')
    errorThreshold = float(config.get('mail','errorThreshold'))



class rubustatDaemon(Daemon):

    def configureGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HEATER_PIN, GPIO.OUT)
        GPIO.setup(AC_PIN, GPIO.OUT)
        GPIO.setup(FAN_PIN, GPIO.OUT)
        subprocess.Popen("echo " + str(HEATER_PIN) + " > /sys/class/gpio/export", shell=True)
        subprocess.Popen("echo " + str(AC_PIN) + " > /sys/class/gpio/export", shell=True)
        subprocess.Popen("echo " + str(FAN_PIN) + " > /sys/class/gpio/export", shell=True)

    def getHVACState(self):
        heatStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
        coolStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
        fanStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())

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

    def cool(self):
        GPIO.output(HEATER_PIN, False)
        GPIO.output(AC_PIN, True)
        GPIO.output(FAN_PIN, True)
        return -1

    def heat(self):
        GPIO.output(HEATER_PIN, True)
        GPIO.output(AC_PIN, False)
        GPIO.output(FAN_PIN, True)
        return 1

    def fan_to_idle(self): 
        #to blow the rest of the heated / cooled air out of the system
        GPIO.output(HEATER_PIN, False)
        GPIO.output(AC_PIN, False)
        GPIO.output(FAN_PIN, True)

    def idle(self):
        GPIO.output(HEATER_PIN, False)
        GPIO.output(AC_PIN, False)
        GPIO.output(FAN_PIN, False)
        #delay to preserve compressor
        time.sleep(360)
        return 0

    if mailEnabled == True:
        def sendErrorMail(self):
            headers = ["From: " + sender,
                       "Subject: " + subject,
                       "To: " + recipient,
                       "MIME-Version: 1.0",
                       "Content-Type: text/html"]
            headers = "\r\n".join(headers)
            session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT) 
            session.ehlo()
            #you may need to comment this line out if you're a crazy person
            #and use non-tls SMTP servers
            session.starttls()
            session.ehlo
            session.login(username, password)
            session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
            session.quit()

    def run(self):
        lastLog = datetime.datetime.now()
        lastMail = datetime.datetime.now()
        self.configureGPIO()
        while True:

            #change cwd to wherever rubustat_daemon is
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)

            indoorTemp = float(getIndoorTemp())
            hvacState = int(self.getHVACState())

            file = open("status", "r")
            targetTemp = float(file.readline())
            mode = file.readline()
            file.close()

            now = datetime.datetime.now()
            logElapsed = now - lastLog
            mailElapsed = now - lastMail

            ### check if we need to send error mail
            #cooling 
            #it's 78, we want it to be 72, and the error threshold is 5 = this triggers
            if mailEnabled == True and (mailElapsed > datetime.timedelta(minutes=20)) and (indoorTemp - float(targetTemp) ) > errorThreshold:
                self.sendErrorMail()
                lastMail = datetime.datetime.now()
                if DEBUG == 1:
                    log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                    log.write("MAIL: Sent mail to " + recipient + " at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                    log.close()

            #heat 
            #it's 72, we want it to be 78, and the error threshold is 5 = this triggers
            if mailEnabled == True and (mailElapsed > datetime.timedelta(minutes=20)) and (float(targetTemp) - indoorTemp ) > errorThreshold:
                self.sendErrorMail()
                lastMail = datetime.datetime.now()
                if DEBUG == 1:
                    log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                    log.write("MAIL: Sent mail to " + recipient + " at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                    log.close()


            #logging actual temp and indoor temp to sqlite database.
            #you can do fun things with this data, like make charts! 
            if logElapsed > datetime.timedelta(minutes=6) and sqliteEnabled:
                c.execute('INSERT INTO logging VALUES(?, ?, ?)', (now, indoorTemp, targetTemp))
                conn.commit()
                lastLog = datetime.datetime.now()

                
            # heater mode
            if mode == "heat":
                if hvacState == 0: #idle
                    if indoorTemp < targetTemp - inactive_hysteresis:
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to heat at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = self.heat()

                elif hvacState == 1: #heating
                    if indoorTemp > targetTemp + active_hysteresis:
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        self.fan_to_idle()
                        time.sleep(30)
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = idle()

                elif hvacState == -1: # it's cold out, why is the AC running?
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = self.idle()

            # ac mode
            elif mode == "cool":
                if hvacState == 0: #idle
                    if indoorTemp > targetTemp + inactive_hysteresis:
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to cool at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = self.cool()

                elif hvacState == -1: #cooling
                    if indoorTemp < targetTemp - active_hysteresis:
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        self.fan_to_idle()
                        time.sleep(30)
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = self.idle()

                elif hvacState == 1: # it's hot out, why is the heater on?
                        if DEBUG == 1:
                            log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                            log.write("STATE: Switching to fan_to_idle at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
                            log.close()
                        hvacState = self.idle()
            else:
                print "It broke."

            #loggin'stuff
            if DEBUG == 1:
                heatStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
                coolStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
                fanStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
                log = open("logs/debug_" + datetime.datetime.now().strftime('%Y%m%d') + ".log", "a")
                log.write("Report at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ":\n")
                log.write("hvacState = " + str(hvacState)+ "\n")
                log.write("indoorTemp = " + str(indoorTemp)+ "\n")
                log.write("targetTemp = " + str(targetTemp)+ "\n")
                log.write("heatStatus = " + str(heatStatus) + "\n")
                log.write("coolStatus = " + str(coolStatus)+ "\n")
                log.write("fanStatus = " + str(fanStatus)+ "\n")
                log.close()
            
            time.sleep(5)


if __name__ == "__main__":
        daemon = rubustatDaemon('rubustatDaemon.pid')
      
        #Setting up logs
        if not os.path.exists("logs"):
            subprocess.Popen("mkdir logs", shell=True)

        if sqliteEnabled == True:
            conn = sqlite3.connect("temperatureLogs.db")
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS logging (datetime TIMESTAMP, actualTemp FLOAT, targetTemp INT)')    

        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        #stop all HVAC activity when daemon stops
                        GPIO.setmode(GPIO.BCM)
                        GPIO.setup(HEATER_PIN, GPIO.OUT)
                        GPIO.setup(AC_PIN, GPIO.OUT)
                        GPIO.setup(FAN_PIN, GPIO.OUT)
                        GPIO.output(HEATER_PIN, False)
                        GPIO.output(AC_PIN, False)
                        GPIO.output(FAN_PIN, False)
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
