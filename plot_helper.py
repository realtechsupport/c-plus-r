# plot_helper.py (python3)
# utilities for graphic display of training and evaluation results
# experiments in knowledge documentation; with an application to AI for ethnobotany
# March 2020
#-------------------------------------------------------------------------------
import os, sys, glob
from pyt_utilities import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy
import pandas
pandas.set_option('display.max_columns', 50)
pandas.set_option('display.width', 1000)

#-------------------------------------------------------------------------------
def plot_training(e_val_loss, e_train_loss, e_val_acc, e_train_acc, training_image):

    ind = [i for i in range(len(e_val_loss))]
    best = 'best eval accuracy: ' + str(numpy.max(e_val_acc)) + '; best train accuracy: ' + str(numpy.max(e_train_acc))
    print(best)

    fig, axs = plt.subplots(2, figsize=(16, 8))
    axs[0].plot(ind, e_val_loss,  marker='x', markersize=14, c='r', linestyle = '--', linewidth=1)
    axs[1].plot(ind, e_val_acc,  marker='x', markersize=14, c='r', linestyle = '--', linewidth=1)
    #axs[2].plot(ind, e_train_loss,  marker='s', markersize=6, c='r', linestyle = '--', linewidth=1)
    #axs[3].plot(ind, e_train_acc,  marker='s', markersize=3, c='r', linestyle = '--', linewidth=1)

    for i in range (0,2):
        axs[i].yaxis.set_major_locator(plt.MaxNLocator(8))
        axs[i].set_ylabel('score')
        axs[i].grid()
        axs[i].set_xlabel('training epochs')

    for ax in axs.flat:
        ax.label_outer()

    text = 'Evaluation loss (top) and accuracy (bottom); \n' + best + '\n'
    fig.suptitle(text, fontsize=18)
    fig.subplots_adjust(top=0.9)
    plt.savefig(training_image)

#------------------------------------------------------------------------------
def plot_toperrors(datapath, testcollection, network, toperrors_filename, toperrors_image, pretrained, nepochs, max_images, ttp):

    columnnames = ['dataset', 'network', 'pretrained', 'training_percentage', 'epochs', 'maximages', 'normalization', 'plant', 'top1e', 'top1val']
    dataset = pandas.read_csv(toperrors_filename, sep=',' , names=columnnames)
    dataset['top1val'] = pandas.to_numeric(dataset['top1val'], errors='coerce')
    #dataset['top3val'] = pandas.to_numeric(dataset['top3val'], errors='coerce')

    pagewidth = 14; pageheight = 6
    plt.rc('axes', labelsize=18)
    plt.rc('axes', titlesize=20)
    plt.rc('xtick', labelsize=16)
    fig = plt.figure(figsize=(pagewidth, pageheight))
    ax = fig.add_axes([0,0,1,1])
    bars_e1 = ax.bar(dataset['plant'], dataset['top1val'], color='lightgray')
    autolabel(bars_e1, ax, 16)

    #bars_e3 = ax.bar(data['plant'], data['top3val'], color='g')
    #autolabel(bars_e3, ax, 14)
    plt.xticks(rotation=0, ha='right')
    plt.grid(b=True, which='major', color='darkgray', linestyle='-')
    plt.ylim(top=100)
    plt.ylabel('percentage')

    titletext = 'TOP-1 error:' + network + ' on '+ testcollection + ': ' + str(nepochs) + ' epochs, ' + str(ttp) + '% training, ' + str(max_images) + ' images per category'
    ax.set_title(titletext,fontsize= 18)
    fig.subplots_adjust(top=0.9)
    plt.savefig(toperrors_image, transparent=True, bbox_inches='tight')

#------------------------------------------------------------------------------
def autolabel(bars, ax, fs):
    for rect in bars:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 0.9*height,'%d' % int(height),ha='center', va='bottom', fontsize=fs)
#-------------------------------------------------------------------------------
