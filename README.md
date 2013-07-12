Rubustat
========

A thermostat controller for Raspberry Pi on Flask

Mostly based off: 
http://makeatronics.blogspot.com/2013/04/thermostat-software.html

but now with user-friendly web interface!

Dependencies:
* pywapi for weather info (sudo pip install pywapi)
* RPi.GPIO (you probably already have it installed on your Pi)
* Flask (sudo apt-get install python-flask on Ubuntu, Debian, and likely other apt based distros)

Our files:

* static/: simple javascripts and pretty pictures.
* templates/: Only form.html for now. It makes the web interface go!
* rubustat-daemon.py: The backend that decides if we need to turn on the AC, heat, or just do nothing because it's nice outside. Handles the GPIO.
* rubustat-web-interface.py: The Flask frontend, and the flagship of this project. Auto launches rubustat-daemon. ***BIG*** buttons because I have no idea how to do decent web design, and want to make it easy for tablet / smartphone users. Function > form! 
* set_temp: a plaintext file for dictating the target temperature. Written to by rubustat-web-interface, and read by rubustat-daemon. Who needs databases?