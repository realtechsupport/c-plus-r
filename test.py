
#!/usr/bin/env python3
# main.py
# Catch+Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
# spring 2020
# tested on ubuntu 18 LTS, kernel 5.3.0

#------------------------------------------------------------------------------
import sys, os, time, shutil, glob
from av_helper import *
from utilities import *
from pyt_utilities import *
from plot_helper import *
#-------------------------------------------------------------------------------
'''
#datapath = '/home/realtech/Desktop/ve_ol_p37/code/c+r_local_may7/results/'
datapath = '/home/realtech/Desktop/temp/'
network = 'Alexnet'
toperrors_filename = 'top_errors.csv'
toperrors_image = 'top_errors_image.jpg'
ttp = 50; max_images = 1000;
nepochs = 2;
testcollection = 'bali-3'
pretrained = True

toperrors_filename  = datapath + toperrors_filename
toperrors_image = datapath + toperrors_image
plot_toperrors(datapath, testcollection, network, toperrors_filename, toperrors_image, pretrained, nepochs, max_images, ttp)

#http://manpages.ubuntu.com/manpages/bionic/man1/aplay.1.html
#https://bbs.archlinux.org/viewtopic.php?id=196525

# arecord -l
**** List of CAPTURE Hardware Devices ****
'''

mic = 'AT2020'
cardn, devicen = mic_info(mic)
dur = 3
output = 'sample.wav'
record_and_playback(dur, cardn, devicen, output)
