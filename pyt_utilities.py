# pyt_utilities.py (python3)
# utilities for CNN training with pytorch;  data preparation, training, evaluation
# added saving checkpoint
# FEB 2020
# sources:
# https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html#load-data
# https://pytorch.org/tutorials/beginner/finetuning_torchvision_models_tutorial.html

#updated normalization mean and std:
#mean [0.4597244970012637, 0.4887084808460421, 0.46925360649661096]
#std [0.20728858675971737, 0.2048932794469992, 0.21645177513430724]
#-------------------------------------------------------------------------------
import os, sys, time, random, itertools
import torch, torchvision
from torch.optim import lr_scheduler
from torch.autograd import Variable
from torchvision import models, datasets, transforms
import torch.nn.functional as F
from torch import utils
import torch.optim as optim
from PIL import Image
import numpy
import array
import urllib, glob, shutil
from shutil import copyfile, copy
from copy import deepcopy
import matplotlib.pyplot as plt

from plot_helper import *
from utilities import *


bali26_class_names = ['aroid', 'bamboo', 'banana', 'cacao', 'cinnamon', 'coffeearabica', 'dragonfruit', 'durian', 'frangipani', 'guava', \
'jackfruit', 'lychee', 'mango',  'mangosteen', 'nilam', 'papaya', 'passiflora', \
'sawo', 'snakefruit', 'starfruit', 'sugarpalm', 'taro', 'vanilla', 'waterguava', 'whitepepper', 'zodia']

#files on pCloud
bali26_alexnet = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/models/bali26_alexnet.pth'
bali26_resnet152 = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/models/bali26_resnet152.pth'
bali26_rexnext50 = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/models/bali26_resnext50.pth'
bali26_samples_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/bali26samples.zip'
bali3_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/bali-3.zip'
bali3B_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/bali-3B.zip'
bali3C_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/bali-3C.zip'
bali3D_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/bali-3D.zip'
tests_zip = 'https://filedn.com/lqzjnYhpY3yQ7BdfTulG1yY/tests.zip'

#-------------------------------------------------------------------------------
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.4597, 0.4887, 0.4692], [0.2072, 0.2048, 0.2164]) #bali26
        #transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.4597, 0.4887, 0.4692], [0.2072, 0.2048, 0.2164]) #bali26
        #transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

predict_transform = transforms.Compose([
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.4597, 0.4887, 0.4692], [0.2072, 0.2048, 0.2164]) #bali26
    #transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

#-------------------------------------------------------------------------------
#simple three layer CNN for 224 x 224 input; reduced alexnet; untrained by default
#https://github.com/pytorch/vision/blob/master/torchvision/models/alexnet.py
class vanillanet(torch.nn.Module):
    def __init__(self, num_classes):
        super(vanillanet, self).__init__()

        self.cnn_layers = torch.nn.Sequential(
            torch.nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            torch.nn.ReLU(inplace=True),
            torch.nn.MaxPool2d(kernel_size=3, stride=2),

            torch.nn.Conv2d(64, 192, kernel_size=5, padding=2),
            torch.nn.ReLU(inplace=True),
            torch.nn.MaxPool2d(kernel_size=3, stride=2),

            torch.nn.Conv2d(192, 256, kernel_size=3, padding=1),
            torch.nn.ReLU(inplace=True),
            torch.nn.MaxPool2d(kernel_size=3, stride=2),
        )

        self.avgpool = torch.nn.AdaptiveAvgPool2d((6, 6))
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(),
            torch.nn.Linear(256 * 6 * 6, 4096),
            torch.nn.ReLU(inplace=True),
            torch.nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.cnn_layers(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return (x)

#-------------------------------------------------------------------------------
def prune_imageset(datapath, categories, limit, randomprune):
    for i in range(0, len(categories)):
        files = list(filter(os.path.isfile, glob.glob(datapath + categories[i] + '/' + "*")))

        if(randomprune == True):
            #random.shuffle(files)
            shuffle(files)
        else:
            files.sort(key=lambda x: os.path.getmtime(x))

        for i in range (0, len(files)):
            if(i < limit):
                pass
            else:
                print("random?, getting rid of: ", randomprune, files[i])
                os.remove(files[i])

#-------------------------------------------------------------------------------
def create_train_val_sets(datapath, categories, percentage):
    train = datapath + 'train/'
    val = datapath + 'val/'

    if not os.path.exists(train):
        os.mkdir(train)
        for k in categories:
            os.mkdir(train + k)
    if not os.path.exists(val):
        os.mkdir(val)
        for k in categories:
            os.mkdir(val + k)

    os.chdir(datapath)

    try:
        i = categories.index('train'); j = categories.index('val')
        p,d,f = next(os.walk(categories[i]))
        del categories[i]; del categories[j]
    except:
        pass

    print('here are the categories: ', categories)

    for i in range(0, len(categories)):
        files = list(filter(os.path.isfile, glob.glob(datapath + categories[i] + '/' + "*")))
        files.sort(key=lambda x: os.path.getmtime(x))

        traininglimit = int(percentage*len(files))
        print('\ncategory: ', categories[i])
        print('number files for training: ', traininglimit)
        print('number files for validation: ', (len(files) - traininglimit))

        for j in range (0, len(files)):
            filename = files[j].split('/')[-1]
            filecatname = categories[i] + '/' + filename
            if(j < traininglimit):
                filecatnametrain = train + filecatname
                shutil.copy(files[j], filecatnametrain)
            else:
                filecatnameval = val + filecatname
                shutil.copy(files[j], filecatnameval)

#-------------------------------------------------------------------------------
#def train_model(checkpointname, model, criterion, optimizer, scheduler, num_epochs, output):
def train_model(app, checkpointname, network, testcollection, model, categories, datapath, epochs, gamma, lr, momentum, max_images, training_percentage, pretrained, training_image, normalization):

    prune_imageset(datapath, categories, max_images, randomprune=True)
    #check if they esist, if so, delete and re-create
    create_train_val_sets(datapath, categories, training_percentage)

    device = ("cuda" if torch.cuda.is_available() else "cpu" )
    image_datasets = {x: datasets.ImageFolder(os.path.join(datapath, x), data_transforms[x]) for x in ['train', 'val']}
    dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,shuffle=True, num_workers=4) for x in ['train', 'val']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes

    model = model.to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr, momentum)
    step_size = 7
    scheduler = lr_scheduler.StepLR(optimizer, step_size, gamma)

    #---------------------------------------------------------------------------
    since = time.time()
    best_acc = 0.0
    e_val_loss = []; e_train_loss = []
    e_val_acc = []; e_train_acc = []

    for epoch in range(epochs):
        print('Epoch {}/{}'.format(epoch, epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                print('training...')
                model.train()  # Set model to training mode
            else:
                print('evaluating...')
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0; running_corrects = 0
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)
                # zero the parameter gradients
                optimizer.zero_grad()
                # forward; track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            print('{} Loss: {:.4f} Acc: {:.4f}'.format(phase, epoch_loss, epoch_acc))
            loss = float('{:.4f}'.format(epoch_loss))
            acc = float('{:.4f}'.format(epoch_acc))

            if(phase == 'train'):
                e_train_loss.append(loss)
                e_train_acc.append(acc)

            if(phase == 'val'):
                e_val_loss.append(loss)
                e_val_acc.append(acc)

            if (phase == 'val' and epoch_acc > best_acc):
                best_acc = epoch_acc
                best_model_wts = deepcopy(model.state_dict())
                checkpoint = {'model': model,'state_dict': model.state_dict(), 'optimizer' : optimizer.state_dict()}

        print()

    time_elapsed = time.time() - since
    model.load_state_dict(best_model_wts)
    torch.save(checkpoint, checkpointname)
    print('Training complete in {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))
    print('\nPlotting results...')
    plot_training(e_val_loss, e_train_loss, e_val_acc, e_train_acc, training_image)

    toperrors_filename = os.path.join(app.config['RESULTS'], 'top_errors.csv')
    tk=3; processor=device; tpp=int(100 * training_percentage)

    get_toperrors(datapath, checkpointname, network, testcollection, predict_transform, tk, processor, toperrors_filename, pretrained, tpp, normalization, epochs, max_images)
    toperrors_image = os.path.join(app.config['RESULTS'], 'top_errors.jpg')
    ttp = int(100*training_percentage)
    plot_toperrors(datapath, testcollection, network, toperrors_filename, toperrors_image, pretrained, epochs, max_images, ttp)

    nwidth = 680; resize_image(training_image, nwidth)
    nwidth = 640; resize_image(toperrors_image, nwidth)

    return (training_image, toperrors_image)

#-------------------------------------------------------------------------------
def get_toperrors(datapath, checkpointname, network, testcollection, predict_transform, tk, processor, toperrors_filename, pretrained, tpp, normalization, epochs, max_images):
    print('\n> Getting top errors <')

    if(pretrained == True):
        if('bali' in normalization):
            comment_t = testcollection + ', ' + network + ', pretrainedyes' + ', ' + str(tpp) + ', ' + str(epochs) + ', ' + str(max_images) + ', ' +  'balinorms'
        else:
            comment_t = testcollection+ ', ' + network + ', pretrainedyes' + ', ' + str(tpp) + ', ' + str(epochs) + ', ' + str(max_images) + ', ' +  ''
    else:
        if('bali' in normalization):
            comment_t = testcollection + ', ' + network + ', pretrainedNO' + ', ' + str(tpp) + ', ' + str(epochs) + ', ' + str(max_images) + ', ' + 'balinorms'
        else:
            comment_t = testcollection + ', ' + network + ', pretrainedNO' + ', ' + str(tpp) + ', ' + str(epochs) + ', ' + str(max_images) + ', ' +  ''

    image_datasets = {x: datasets.ImageFolder(os.path.join(datapath, x), data_transforms[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes

    try:
        model = load_checkpoint(checkpointname, processor)
    except:
        print('That model does not exist... ')
        exit()

    for i in range (0, len(class_names)):
        fulldatapath = datapath + 'val/' + class_names[i] + '/'
        path, dirs, files = next(os.walk(fulldatapath))
        limit = len(files)
        top1 = 0; topN = 0; tk = 3

        for j in range (0, limit):
            image_path = next(itertools.islice(os.scandir(fulldatapath), j, None)).path
            predictions, percentage, outcategory = predict_image(image_path, model, predict_transform, class_names, tk, processor)
            topN_ind = predictions[1].tolist()[0]
            top1_ind = topN_ind[0]
            input = image_path.split('/')[-2], image_path.split('/')[-1]

            #check input[1] to find problematic images / categories of confusion
            #print('\ninput: ', input); print('output: ', outcategory, percentage)

            if(class_names[top1_ind] == input[0]):
                top1 = top1 + 1
            #if(check_topN(class_names, topN_ind, tk, input[0]) == 1):
            #    topN = topN + 1

        top1_score = float(top1 / limit)
        top1_error = 100*float("%.3f" %(1.0 - top1_score))
        #topN_score = float(topN / limit)
        #topN_error = 100*float("%.3f" %(1.0 - topN_score))
        #comment = comment_t + ', ' + str(class_names[i])  + ', top1-error, ' + str(top1_error) + ', top' + str(tk) + '-error, ' + str(topN_error)
        comment = comment_t + ', ' + str(class_names[i])  + ', top1-error, ' + str(top1_error)
        print(comment)
        write2file(toperrors_filename, comment)

#-------------------------------------------------------------------------------
def predict_image(image_path, model, predict_transform, class_names, tk, processor):
    img = Image.open(image_path)
    img_t = predict_transform(img)

    if((processor == 'gpu') or (processor == 'cuda')):
        batch_t = torch.unsqueeze(img_t, 0).cuda()
    else:
        batch_t = torch.unsqueeze(img_t, 0).cpu()
    model.eval()
    output = model(batch_t)

    predictions = output.topk(tk,1,largest=True,sorted=True)
    _, index = torch.max(output, 1)
    t_percentage = torch.nn.functional.softmax(output, dim=1)[0] * 100
    percentage = t_percentage[index[0]].item()
    percentage = '%.2f'%(percentage)
    category = class_names[index[0]]

    return(predictions, percentage, category)

#-------------------------------------------------------------------------------
def check_topN(class_names, topNlist, tk, input):
    topN = 0
    for i in range (0, len(topNlist)):
        if(class_names[topNlist[i]] == input):
            topN = 1
            break

    return(topN)

#-------------------------------------------------------------------------------
def load_checkpoint(filepath, processor):
    if(processor == 'gpu'):
        checkpoint = torch.load(filepath)
    else:
        checkpoint = torch.load(filepath, map_location=torch.device('cpu'))

    model = checkpoint['model']
    model.load_state_dict(checkpoint['state_dict'])
    for parameter in model.parameters():
        parameter.requires_grad = False

    model.eval()
    return (model)

#-------------------------------------------------------------------------------
def resize_image(inputimage, newwidth):
    img = Image.open(inputimage)
    wpercent = (newwidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    resized_image = img.resize((newwidth,hsize), Image.ANTIALIAS)
    resized_image.save(inputimage)

#-------------------------------------------------------------------------------
