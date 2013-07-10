#! /bin/bash
#shamelessly stolen and modified from http://makeatronics.blogspot.com/2013/04/thermostat-software.html
if [ "$1" = "outdoor_temp" ]
	then
	METRIC=0 # 0 for F, 1 for C
	ZIP=37216
	curl -s -m 20 http://rss.accuweather.com/rss/liveweather_rss.asp\?metric\=${METRIC}\&locCode\=${ZIP} | grep -i -m1 'currently' | grep -o '\-\?[0-9]\+'
fi
if [ "$1" = "indoor_temp" ]
	then
	#TODO: implement when hardware arrives
	echo 70
fi
if [ "$1" = "get_state" ]
	then
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
fi
if [ "$1" = "cool" ]
	then
	echo 0 > /sys/class/gpio/gpio23/value # heater
	echo 1 > /sys/class/gpio/gpio24/value # AC
	echo 1 > /sys/class/gpio/gpio25/value # fan
fi
if [ "$1" = "heat" ]
	then
	echo 1 > /sys/class/gpio/gpio23/value # heater
	echo 0 > /sys/class/gpio/gpio24/value # AC
	echo 1 > /sys/class/gpio/gpio25/value # fan
fi
if [ "$1" = "fan_to_idle" ]
	then
	echo 0 > /sys/class/gpio/gpio23/value # heater
	echo 0 > /sys/class/gpio/gpio24/value # AC
	echo 1 > /sys/class/gpio/gpio25/value # fan
fi
if [ "$1" = "idle" ]
	then
	echo 0 > /sys/class/gpio/gpio23/value # heater
	echo 0 > /sys/class/gpio/gpio24/value # AC
	echo 0 > /sys/class/gpio/gpio25/value # fan
fi
