#! /bin/bash
#shamelessly stolen from http://makeatronics.blogspot.com/2013/04/thermostat-software.html
HEAT=$(cat /sys/class/gpio/gpio23/value)
AC=$(cat /sys/class/gpio/gpio24/value)
FAN=$(cat /sys/class/gpio/gpio25/value)
 
if [ $HEAT == 0 -a $AC == 0 -a $FAN == 0 ]; then
    echo 0 # idle
elif [ $HEAT == 1 -a $AC == 0 ]; then
    echo 1 # heater acive
elif [ $HEAT == 0 -a $AC == 1 ]; then
    echo -1 # AC active
else
    echo 2 # something is wrong...
fi