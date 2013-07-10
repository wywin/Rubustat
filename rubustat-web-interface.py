#!/usr/bin/python
import pywapi
import subprocess


from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#start the daemon in the background
subprocess.call("./rubustat-daemon.py", shell=True)

def getWeather():
    result = pywapi.get_weather_from_yahoo( "37216" , units = 'imperial' )
    string = result['html_description']
    string = string.replace("\n", "")
    string = string.replace("(provided by <a href=\"http://www.weather.com\" >The Weather Channel</a>)<br/>", "")
    string = string.replace("<br /><a href=\"http://us.rd.yahoo.com/dailynews/rss/weather/Nashville__TN/*http://weather.yahoo.com/forecast/USTN0357_f.html\">Full Forecast at Yahoo! Weather</a><BR/><BR/>", "")
    return string

@app.route('/')
def my_form():
    f = open("set_temp", "r")
    targetTemp = f.readline()
    f.close()
    weatherString = getWeather()
    indoor_temp = subprocess.check_output("./etc.sh indoor_temp")
    return render_template("form.html", targetTemp = targetTemp, weatherString = weatherString)

@app.route("/", methods=['POST'])
def my_form_post():

    text = request.form['text']
    newTargetTemp = text.upper()
    f = open("set_temp", "w")
    f.write(newTargetTemp)
    f.close()
    flash("New temperature of " + newTargetTemp + " set!")
    return redirect(url_for('my_form'))

if __name__ == "__main__":
    app.run()