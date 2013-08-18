Rubustat
========

A thermostat controller for Raspberry Pi on Flask

Mostly based off: 
http://makeatronics.blogspot.com/2013/04/thermostat-software.html

but now with user-friendly web interface!

#Dependencies
* RPi.GPIO (you probably already have it installed on your Pi)
* Flask (sudo apt-get install python-flask on Ubuntu, Debian, and likely other apt based distros)

##Optional (required if enabled in config.txt)
* sqlite for less-sloppy logging (sudo apt-get install python-sqlite sqlite3)
* pywapi for weather info (sudo pip install pywapi)

###Credits
http://matthewjamestaylor.com/blog/equal-height-columns-2-column.htm

https://github.com/ftlabs/fastclick

http://proto.io/freebies/onoff/

http://blog.jacobean.net/?p=678

http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

http://segfault.in/2010/12/sending-gmail-from-python/