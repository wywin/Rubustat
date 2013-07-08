#! /bin/bash
#shamelessly stolen from http://makeatronics.blogspot.com/2013/04/thermostat-software.html

echo 0 > /sys/class/gpio/gpio23/value # heater
echo 0 > /sys/class/gpio/gpio24/value # AC
echo 0 > /sys/class/gpio/gpio25/value # fan