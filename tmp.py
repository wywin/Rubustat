import sqlite3
import simplejson as json
import urllib2
import pywapi
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

result = pywapi.get_weather_from_yahoo( "37216" , units = 'imperial' )
print result['html_description']
