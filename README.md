Rubustat
========

A thermostat controller for Raspberry Pi on Flask

Mostly based off:
http://makeatronics.blogspot.com/2013/04/thermostat-software.html

but now with user-friendly web interface!

***NOTE*** I am not a designer, and this UI was primarily for my dad / his phone. Small screens + aging eyes
means ***BIG NUMBERS!***

##Contact

I would LOVE if you [threw me an email](mailto:rubustatcontact@wyattwinters.com) if you decide to use any of this code for your own RPi-based thermostat.
It doesn't have to be long or involved, but knowing my work is used outside of my house would be great!

If you want to donate, you can send me BTC at 1Dz6YehDXZk2GBCYi9SfWRSPZAEndmQxk5, or donate to other, bigger open source projects that will actually use the funding to further development. On the topic of RPi, why not [Raspbian](http://www.raspbian.org/RaspbianDonate)?

##Forks!

@aneisch has forked this project, and is adding cool stuff like scheduling! You can find his fork either from the fork menu, or just click [here](https://github.com/aneisch/Rubustat). Thanks for doing cool stuff @aneisch!

While not strictly a fork, @madbrenner has created [PyStat](https://gitlab.com/madbrenner/PyStat) which features a [much nicer UI](https://imgur.com/a/7vkZO). As an added bonus, the code appears to be *WAY LESS* of a hacky mess compared to mine. You should really check it out. It's probably what you should use instead.

##Pictures!

There's a picture of my hardware, and screenshots of the UI on desktop and mobile browsers over on [my blog](http://wyattwinters.com/rubustat-the-raspberry-pi-thermostat.html).

##Hardware

* Raspberry Pi (A, B, or B+ should work)
* Some way to hook up the GPIO pins to the thermostat hookups in your wall (I used this [nice pre-made board](http://makeatronics.blogspot.com/2013/06/24v-ac-solid-state-relay-board.html) explicitly for this purpose!)
* If using the board above, you should also get everything off the [parts list](https://docs.google.com/spreadsheet/ccc?key=0AtDuE3f5Cnm7dEU3MWFEeTU0RnZyTUNfVUxrX1FVdXc&usp=sharing)(Google Docs, which now requires an account?)
* A temperature sensor. This was written with the [DS18B20](https://www.adafruit.com/products/374), but it should be pretty easy to code up your own function for your specific sensor your have on hand
* Some way to hook your RPi up to your network. This project is infinitely more helpful when you can access the web interface.

##Dependencies
* RPi.GPIO (you probably already have it installed on your Pi)
* Flask (sudo apt-get install python-flask on Ubuntu, Debian, Raspbian, and likely other apt based distros)
* kernel modules w1-gpio and w1-therm (unsure if these are default in Raspbian, but make sure you have them)

###Optional (required if enabled in config.txt)
* sqlite for less-sloppy logging (sudo apt-get install python-sqlite sqlite3)
* pywapi for weather info (sudo pip install pywapi)

##Installation

1. git clone https://github.com/wywin/Rubustat.git
2. copy config.txt.template to config.txt and edit with appropriate values
3. copy mailconf.txt.template to mailconf.txt and fill in values (if using error mails)
4. (optional) add web interface to startup. I added the lines

```
modprobe w1-gpio
```

```
modprobe w1-therm
```

```
/usr/bin/python /home/pi/src/Rubustat/rubustat_web_interface.py &
```

to /etc/rc.local, and it works without a hitch. Although the modprobes are also in getIndoorTemp, I added them
before the web interface call because it was throwing fits without the pre-call modprobes... ¯\\_(ツ)_/¯

###Code Map

#####The configs
* config.txt.template - the main config file, heavily commented to help you make sense of it. Enable optional features here!
* mailconf.txt.template - a template for the mail configuration. Fill in the values, enable mail in config.txt, and
  get helpful error email alerts! These are used to hopefully inform you of potential hardware issues. This is from when
  one of my alligator clips fell off, and it was really hot when I got home.
* status - target temperature (in degrees F, because I'm an awful American) and mode (cool or heat) - this can be edited by hand,
  or via the web UI


#####The code
* daemon.py - the underlying daemon class from [here](http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/).
  I added on some stale-pid checking.
* rubustat_daemon.py - the proper daemon. Reads from status, controls the GPIO pins, and does email notifications, if enabled, and sqlite logging, if enabled
* rubustat_web_interface.py - the web interface. Auto launches rubustat_daemon.py, and writes to status. Optionally displays local weather conditions,
  dictated by the ZIP code in config.txt. You will have to adjust getWeather to strip off the annoying link from the bottom of the API result.
* static/ and templates/ - various html, css, and js to make the web interface fancy. NOT AT ALL standards compliant, but it works, so I'm happy with it.

####Credits
In no particular order:

http://matthewjamestaylor.com/blog/equal-height-columns-2-column.htm

https://github.com/ftlabs/fastclick

http://proto.io/freebies/onoff/

http://blog.jacobean.net/?p=678

http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

http://segfault.in/2010/12/sending-gmail-from-python/

http://tmpvar.com/markdown.html