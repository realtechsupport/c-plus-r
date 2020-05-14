# get mean and std of color bands in our image set for the pytorch normalization
# march 2020
#-------------------------------------------------------------------------------
import os, sys, glob
import numpy
from PIL import Image
from pyt_utilities import *
#---------------------------------------------------------
filename = 'norm-values.txt'
datapath = '/your_datapath/'

b_mean=[]; r_mean=[]; g_mean=[]; b_std=[]; r_std=[]; g_std=[]
path, dirs, files = next(os.walk(datapath))

for i in range (0, len(dirs)):
    ppath, ddirs, ffiles = next(os.walk(datapath+dirs[i]))
    print('inside: ', dirs[i])
    #for j in range (0, 2):
    for j in range (0, len(ffiles)):
        im = Image.open(datapath+dirs[i]+'/'+ffiles[j])
        n_im = numpy.array(im)
        b, g, r = n_im[:, :, 0], n_im[:, :, 1], n_im[:, :, 2]

        im_b_mean = numpy.mean(b)
        im_g_mean = numpy.mean(g)
        im_r_mean = numpy.mean(r)

        im_b_std = numpy.std(b)
        im_g_std = numpy.std(g)
        im_r_std = numpy.std(r)

        b_mean.append(im_b_mean)
        g_mean.append(im_g_mean)
        r_mean.append(im_r_mean)

        b_std.append(im_b_std)
        g_std.append(im_g_std)
        r_std.append(im_r_std)

b_m_n = numpy.mean(b_mean) / 255
g_m_n = numpy.mean(im_g_mean) / 255
r_m_n = numpy.mean(im_r_mean) / 255

b_std_n = numpy.mean(b_std) / 255
g_std_n = numpy.mean(g_std) / 255
r_std_n = numpy.mean(r_std) / 255

comment = str([b_m_n, g_m_n, r_m_n]) + str([b_std_n, g_std_n, r_std_n])
write2file(filename, comment)
print('\n\nFINISHED calculations....')
