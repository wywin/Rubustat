#!/usr/bin/python
import pywapi
import subprocess
from getIndoorTemp import getIndoorTemp

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

ZIP = 37216

#start the daemon in the background
subprocess.Popen("./rubustat_daemon.py", shell=True)

def getWeather():
    result = pywapi.get_weather_from_yahoo( str(ZIP), units = 'imperial' )
    string = result['html_description']
    string = string.replace("\n", "")
    string = string.replace("(provided by <a href=\"http://www.weather.com\" >The Weather Channel</a>)<br/>", "")
    string = string.replace("<br /><a href=\"http://us.rd.yahoo.com/dailynews/rss/weather/Nashville__TN/*http://weather.yahoo.com/forecast/USTN0357_f.html\">Full Forecast at Yahoo! Weather</a><BR/><BR/>", "")
    return string

@app.route('/')
def my_form():
    f = open("status", "r")
    targetTemp = f.readline().strip()
    mode = f.readline()
    f.close()
    weatherString = getWeather()
    indoor_temp = getIndoorTemp()
    
    #find out what mode the system is in, and set the switch accordingly
    #the switch is in the "cool" position when the checkbox is checked
    if mode == "heat":
        checked = ""
    elif mode == "cool":
        checked = "checked=\"checked\""
    else:
        checked = "Something broke"
    return render_template("form.html", targetTemp = targetTemp, \
                                        weatherString = weatherString, \
                                        checked = checked, \
                                        indoor_temp = indoor_temp)

@app.route("/", methods=['POST'])
def my_form_post():

    text = request.form['text']
    mode = "heat"
    #default mode to heat 
    #cool if the checkbox is returned, it is checked
    #and cool mode has been selected
    if 'onoffswitch' in request.form:
        mode = "cool"
    #TODO: input validation
    newTargetTemp = text.upper()
    f = open("status", "w")
    f.write(newTargetTemp + "\n" + mode)
    f.close()
    flash("New temperature of " + newTargetTemp + " set!")
    return redirect(url_for('my_form'))

if __name__ == "__main__":
    app.run()