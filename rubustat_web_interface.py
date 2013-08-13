#!/usr/bin/python
import pywapi
import os
import subprocess
import re
import ConfigParser

from getIndoorTemp import getIndoorTemp

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify

app = Flask(__name__)
#hard to be secret in open source... >.>
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

config = ConfigParser.ConfigParser()
config.read("config.txt")
ZIP = config.get('main','ZIP')
HEATER_PIN = int(config.get('main','HEATER_PIN'))
AC_PIN = int(config.get('main','AC_PIN'))
FAN_PIN = int(config.get('main','FAN_PIN'))

#start the daemon in the background
subprocess.Popen("/usr/bin/python rubustat_daemon.py start", shell=True)

def getWeather():
    result = pywapi.get_weather_from_yahoo( str(ZIP), units = 'imperial' )
    string = result['html_description']
    string = string.replace("\n", "")

    #You will likely have to change these strings, unless you don't mind the additional garbage at the end.
    string = string.replace("(provided by <a href=\"http://www.weather.com\" >The Weather Channel</a>)<br/>", "")
    string = string.replace("<br /><a href=\"http://us.rd.yahoo.com/dailynews/rss/weather/Nashville__TN/*http://weather.yahoo.com/forecast/USTN0357_f.html\">Full Forecast at Yahoo! Weather</a><BR/><BR/>", "")
    return string

def getWhatsOn():
    heatStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
    coolStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
    fanStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())

    heatString = "<p id=\"heat\"> OFF </p>"
    coolString = "<p id=\"cool\"> OFF </p>"
    fanString = "<p id=\"fan\"> OFF </p>"
    if heatStatus == 1:
        heatString = "<p id=\"heatOn\"> ON </p>"
    if coolStatus == 1:
        coolString = "<p id=\"coolOn\"> ON </p>"
    if fanStatus == 1:
        fanString = "<p id=\"fanOn\"> ON </p>"

    return heatString + coolString + fanString

@app.route('/')
def my_form():
    f = open("status", "r")
    targetTemp = f.readline().strip()
    mode = f.readline()
    f.close()
    try:
        weatherString = getWeather()
    except:
        weatherString = "Couldn't get remote weather info! <br><br>"

    whatsOn = getWhatsOn()

    #find out what mode the system is in, and set the switch accordingly
    #the switch is in the "cool" position when the checkbox is checked

    try:
        with open('rubustatDaemon.pid'):
            pid = int(subprocess.Popen("cat rubustatDaemon.pid", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
            try:
                os.kill(pid, 0)
                daemonStatus="<p id=\"daemonRunning\"> Daemon is running. </p>"
            except OSError:
                daemonStatus="<p id=\"daemonNotRunning\"> DAEMON IS NOT RUNNING. </p>"
    except IOError:
        daemonStatus="<p id=\"daemonNotRunning\"> DAEMON IS NOT RUNNING. </p>"


    if mode == "heat":
        checked = ""
    elif mode == "cool":
        checked = "checked=\"checked\""
    else:
        checked = "Something broke"
    return render_template("form.html", targetTemp = targetTemp, \
                                        weatherString = weatherString, \
                                        checked = checked, \
                                        daemonStatus = daemonStatus, \
                                        whatsOn = whatsOn)

@app.route("/", methods=['POST'])
def my_form_post():

    text = request.form['target']
    mode = "heat"

    #default mode to heat 
    #cool if the checkbox is returned, it is checked
    #and cool mode has been selected

    if 'onoffswitch' in request.form:
        mode = "cool"
    newTargetTemp = text.upper()
    match = re.search(r'^\d{2}$',newTargetTemp)
    if match:
        f = open("status", "w")
        f.write(newTargetTemp + "\n" + mode)
        f.close()
        flash("New temperature of " + newTargetTemp + " set!")
        return redirect(url_for('my_form'))
    else:
        flash("That is not a two digit number! Try again!")
        return redirect(url_for('my_form'))

@app.route('/_liveTemp', methods= ['GET'])
def updateTemp():

    indoor_temp=getIndoorTemp()
    rounded_indoor_temp = round(indoor_temp,1)
    return jsonify(rounded_indoor_temp=rounded_indoor_temp)

@app.route('/_liveWhatsOn', methods= ['GET'])
def updateWhatsOn():

    return getWhatsOn()


if __name__ == "__main__":
    app.run("0.0.0.0", port=80, debug=True)
