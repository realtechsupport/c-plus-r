# pyt_load+eval.py (python3)
# CNNs with pytorch
# load a saved network and evaluate on the validation set
# FEB 2020
# sources:
# https://pytorch.org/tutorials/beginner/finetuning_torchvision_models_tutorial.html

# set the following variables according to your setup; they must match the setting used to train the network !
# dataset, datapath, network, pretrained flag and category names

# set the following variables to change how the training unfolds; they must match the setting used to train the network !
# num_epochs, img_limit, training_percentage
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
import os, sys, time, random, itertools
from datetime import datetime
from pyt_utilities import *

#must be same as corresponing training run !!
dataset = 'your_dataset'
network = 'the_network'
pretrained = True;
balinorms = True;           #true, if you are normalizing with the means and stds calculated for the bali26 dataset - see pyt_utilities.py
num_epochs = 20;
offset = 0; img_limit = 2500;
training_percentage = 0.5;
tpp = int(100 * training_percentage)
#-------------------------------------------------------------------------------

path = os.getcwd() + '/'
datapath = 'your_datapath/'
resultspath = '/your_datapath/' + 'results/'
if not os.path.exists(resultspath):
    os.makedirs(resultspath)

if(pretrained == True):
    if(balinorms == True):
        checkpointname = path + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '.jpg'
        comment_t = dataset + ', ' + network + ', pretrainedyes_t' + str(tpp) + ', e' + str(num_epochs) + ', lim' + str(img_limit) + '_balinorms'
        filename = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '.csv'
    else:
        checkpointname = path + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '.jpg'
        comment_t = dataset + ', ' + network + ', pretrainedyes_t' + str(tpp) + ', e' + str(num_epochs) + ', lim' + str(img_limit)
        filename = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '.csv'
else:
    if(balinorms == True):
        checkpointname = path + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '.jpg'
        comment_t = dataset + ', ' + network + ', pretrainedNO_t' + str(tpp) + ', e' + str(num_epochs) + ', lim' + str(img_limit) + '_balinorms'
        filename = resultspath + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms' + '.csv'
    else:
        checkpointname = path + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) +'_lim' + str(img_limit) +  '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) +'_lim' + str(img_limit) +  '.jpg'
        comment_t = dataset + ', ' + network + ', pretrainedNO_t' + str(tpp) + ', e' + str(num_epochs) + ', lim' + str(img_limit)
        filename = resultspath + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '.csv'


image_datasets = {x: datasets.ImageFolder(os.path.join(datapath, x), data_transforms[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

try:
    model = load_checkpoint(checkpointname)
except:
    print('That model does not exist... ')
    exit()

print('\nLoading: ', checkpointname)
print('\n> Predicting class of input images <')

for i in range (0, len(class_names)):
    plantdatapath = datapath + 'val/' + class_names[i] + '/'
    path, dirs, files = next(os.walk(plantdatapath))
    limit = len(files)
    top1 = 0; topN = 0; tk = 3

    for j in range (0, limit):
        image_path = next(itertools.islice(os.scandir(plantdatapath), j, None)).path
        predictions, percentage, outcategory = predict_image(image_path, model, predict_transform, class_names, tk)
        topN_ind = predictions[1].tolist()[0]
        top1_ind = topN_ind[0]

        input = image_path.split('/')[-2], image_path.split('/')[-1]

        #you can check input[1] to find problematic images / categories of confusion
        #print('\ninput: ', input); print('output: ', outcategory, percentage)

        if(class_names[top1_ind] == input[0]):
            top1 = top1 + 1

        if(check_topN(class_names, topN_ind, tk, input[0]) == 1):
            topN = topN + 1

    top1_score = float(top1 / limit)
    topN_score = float(topN / limit)
    top1_error = 100*float("%.3f" %(1.0 - top1_score))
    topN_error = 100*float("%.3f" %(1.0 - topN_score))

    comment = comment_t + ', ' + str(class_names[i])  + ', top1-error, ' + str(top1_error) + ', top' + str(tk) + '-error, ' + str(topN_error)
    print(comment + '\n')
    write2file(filename, comment)
