#! /bin/bash
#shamelessly stolen from http://makeatronics.blogspot.com/2013/04/thermostat-software.html
METRIC=0 # 0 for F, 1 for C
ZIP=(your zip here)
 
curl -s -m 20 http://rss.accuweather.com/rss/liveweather_rss.asp\?metric\=${METRIC}\&locCode\=${ZIP} | grep -i -m1 'currently' | grep -o '\-\?[0-9]\+'