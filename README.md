Rubustat
========

A thermostat controller for Raspberry Pi on Flask

Mostly based off: 
http://makeatronics.blogspot.com/2013/04/thermostat-software.html

but now with user-friendly web interface!

***NOTE*** I am not a designer, and this UI was primarily for my dad / his phone. Small screens + aging eyes
means ***BIG NUMBERS!***

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

##Contact

I would LOVE if you [threw me an email](mailto:rubustatcontact@wyattwinters.com) if you decide to use any of this code for your own RPi-based thermostat.
It doesn't have to be long or involved, but knowing my work is used outside of my house would be great!


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
* rubustat_daemon.py - the proper daemon. Reads from status, controls the GPIO pins, and does email and sqlite logging, if enabled
* rubustat_web_interface.py - the web interface. Auto launches rubustat_daemon.py, and writes to status. Optionally displays local weather conditions,
  dictated through ZIP in config.txt. You will have to adjust getWeather to strip off the annoying link from the bot.
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