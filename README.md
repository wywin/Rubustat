Rubustat
========

A thermostat controller for Raspberry Pi on Flask

Mostly based off: 
http://makeatronics.blogspot.com/2013/04/thermostat-software.html

but now with user-friendly web interface!

Dependencies:
* pywapi for weather info (sudo pip install pywapi)
* Flask (sudo apt-get install python-flask on Ubuntu, Debian, and likely other apt based distros)

Our files:

* etc.sh: Various Bash stuff to control the GPIO, get weather data from the internet and our thermometer (also on GPIO), and other stuff I don't really know how to do in Python very well
* rubustat-daemon.py: The backend that decides if we need to turn on the AC, heat, or just hang out because it's nice outside. Talks to etc.sh a lot!
* rubustat-web-interface.py: The Flask frontend, and the flagship of this project. Auto launches rubustat-daemon. ***BIG*** buttons because I have no idea how to do decent web design, and want to make it easy for tablet / smartphone users. Function > form! 
* set_temp: a plaintext file for dictating the target temperature. Written to by rubustat-web-interface, and read by rubustat-daemon. Who needs databases?