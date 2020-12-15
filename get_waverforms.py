#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 14:18:20 2020

@author: veronica
"""
from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
from obspy.clients.fdsn.mass_downloader import CircularDomain, \
    Restrictions, RectangularDomain, MassDownloader
import obspy
import pandas as pd
import datetime
import numpy as np
from obspy import read_events
import os
from datetime import timedelta
from obspy import UTCDateTime

currentDirectory = os.getcwd()
folder = currentDirectory + 'path' #folder where data will be saved after downloading.
events_catalogue = folder + 'Events.xml'
mseed_storage = folder + '/data/'
stationxml_storage = folder + '/stations/'
output = 'MSEED'

## == Data Parameters == ##
client = Client("IRIS")
provider = 'IRIS'
channels = 'HH?,HN?'
t1=obspy.UTCDateTime('2019-10-01T00:00:00')
t2 =obspy.UTCDateTime('2019-12-01T00:00:00')

minlat = 31
maxlat = 31.5
minlong = -104
maxlong = -103

## == Download Event's Catalogue of events == #
events = client.get_events(starttime=t1, endtime=t2,minlatitude=minlat, maxlatitude=maxlat,
                             minlongitude=minlong, maxlongitude=maxlong )
print("found %s event(s):" % len(events))
## == Write events' catalogue to an xml file == ##
events.write(folder + '/Events.xml', format = 'QUAKEML')

## == Download Stations' Catalogue == #
inv=client.get_stations(network = 'TX', station='XX', minlatitude=minlat, maxlatitude=maxlat,
                          minlongitude=minlong, maxlongitude=maxlong,level='station')
print(inv)
## == Write stations' catalogue to an xml file == ##
inv.write(folder + '/Stations.xml', format = 'STATIONXML')

## == Get stations CSV File (not required) == #
inv.write(folder + '/Stations.csv', level='station', format = 'STATIONTXT')  


## == Download waveforms, organize in folders == ##
for event in events:
    origin = event.origins[0].time.datetime #get time of event
    t1 = origin - timedelta(seconds = 10) #subtract 10 seconds for waveform
    t2 = origin + timedelta(seconds = 30) #add 10 seconds for waveform
    
    # = Make folders for each day of events = #
    tree1 = origin.strftime("%Y")
    output = mseed_storage + tree1 
    if not os.path.exists(output):
        os.mkdir(output)
    tree2 = origin.strftime("%m")
    output = output + '/' + tree2
    if not os.path.exists(output):
        os.mkdir(output)
    tree3 = origin.strftime("%d")
    output = output + '/' + tree3
    if not os.path.exists(output):
        os.mkdir(output)
    tree4 = origin.strftime('%Y-%m-%d-%H-%M-%S')
    output = output + '/' + tree4
    if not os.path.exists(output):
        os.mkdir(output)         
          
    # = Loop through each station and get waveforms = #    
    for i in range(len(inv.networks[0].stations)):
        #GET STATATION DATA
        station = inv.networks[0].stations[i].get_contents()
        station1 = next(iter(station.values()))
        station1 = station1[0][0:4]
        try:   
            st = client.get_waveforms("TX", station1, "00", "HH*", 
                                      UTCDateTime(t1), UTCDateTime(t2))
            tt = origin.timetuple() #get julian date for naming convention
            filename = '.'.join((
                                str(origin.year),str(tt.tm_yday).zfill(3),
                                str(origin.hour).zfill(2),str(origin.minute).zfill(2),
                                str(origin.second).zfill(2),
                                str(origin.microsecond)[:4],
                                'TX',str(station1),'mseed'
                            ))
        # filename = str(t1) +'_' + str(i) +  '_TX.mseed'
            st.write(output + '/' + filename, format='MSEED')
        except: 
            print('no data here')
