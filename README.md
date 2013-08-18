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
2. edit config.txt with appropriate values
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


####Credits
In no particular order:

http://matthewjamestaylor.com/blog/equal-height-columns-2-column.htm

https://github.com/ftlabs/fastclick

http://proto.io/freebies/onoff/

http://blog.jacobean.net/?p=678

http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

http://segfault.in/2010/12/sending-gmail-from-python/

http://tmpvar.com/markdown.html