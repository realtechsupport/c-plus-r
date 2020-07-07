# pyt_train+save.py (python3)
# CNNs with pytorch
# prepare data, load data, select and train network; evaluate on some images
# FEB - MARCH 2020

# set the following variables according to your setup:
# dataset, datapath, network, pretrained flag and category names

# set the following variables to change how the training unfolds:
# num_epochs, img_limit, training_percentage
#-------------------------------------------------------------------------------
import os, sys, time
from pyt_utilities import *

# variables
dataset = 'your_dataset'
network = 'the_network'
pretrained = True;
balinorms = True;           #I changed the normalization based on the bali-26 collection. See create_norms.py

num_epochs = 20;
offset = 0; img_limit = 1000; randomprune = True;
training_percentage = 0.5;
tpp = int(100 * training_percentage)
#-------------------------------------------------------------------------------
datapath = '/your_datapath/' + dataset + '/'
#enter  the list of categories / folder names in the archive
categories = ['cat1', 'cat2', 'cat3']
#-------------------------------------------------------------------------------

path = os.getcwd() + '/'
resultspath = path + 'results/'
if not os.path.exists(resultspath):
    os.makedirs(resultspath)

if(pretrained == True):
    if(balinorms == True):
        checkpointname = path + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '.jpg'
    else:
        checkpointname = path + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyes_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '.jpg'
else:
    if(balinorms == True):
        checkpointname = path + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedyNO_t' + str(tpp) + '_e' + str(num_epochs) + '_lim' + str(img_limit) + '_balinorms'+ '.jpg'
    else:
        checkpointname = path + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) +'_lim' + str(img_limit) +  '_checkpoint.pth'
        output = resultspath + dataset + '_' + network + '_pretrainedNO_t' + str(tpp) + '_e' + str(num_epochs) +'_lim' + str(img_limit) +  '.jpg'

#-------------------------------------------------------------------------------
#1. do only once; prepare the training and validation image sets
prune_imageset(datapath, categories, img_limit, offset, randomprune)
create_train_val_sets(datapath, categories, training_percentage)

#2. load the data
image_datasets = {x: datasets.ImageFolder(os.path.join(datapath, x), data_transforms[x]) for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,shuffle=True, num_workers=4) for x in ['train', 'val']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

device = ("cuda" if torch.cuda.is_available() else "cpu" )

#3. train the network
#if running on a multi pgu computer, try setting ngpu True for better performance.
ngpu = False

if(network == 'vanillanet'):
    model = vanillanet(len(class_names))

elif(network == 'alexnet'):
    model = models.alexnet(pretrained=pretrained)
    model.classifier[6] = torch.nn.Linear(4096,len(class_names))

elif(network == 'squeezenet'):
    model = models.squeezenet1_1(pretrained=pretrained)
    model.classifier[1] = torch.nn.Conv2d(512, len(class_names), kernel_size=(1,1), stride=(1,1))

elif(network == 'resnet18'):
    model = models.resnet18(pretrained=pretrained)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, len(class_names))

elif(network == 'resnet152'):
    model = models.resnet152(pretrained=pretrained)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, len(class_names))
    if(ngpu):
        print('using all gpus available')
        model = torch.nn.DataParallel(model, device_ids=[0,1,2,3]).cuda()

elif(network == 'resnext50'):
    model = models.resnext50_32x4d(pretrained=pretrained)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, len(class_names))
    if(ngpu):
        print('using all gpus available')
        model = torch.nn.DataParallel(model, device_ids=[0,1,2,3]).cuda()

elif(network  == 'inception'):
    #NOT TESTED... Inception v3 expects (299,299) images and has auxiliary output
    model = models.inception_v3(pretrained=pretrained)
    set_parameter_requires_grad(model, feature_extract)
    num_ftrs = model.AuxLogits.fc.in_features
    model.AuxLogits.fc = nn.Linear(num_ftrs, len(class_names))
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs,num_classes)
    input_size = 299

else:
    print("Invalid model name, exiting...")
    exit()

print('\nthe dataset is: ', dataset)
print('the network is: ', network)
print('pretrained network: ', pretrained)
print('training and validation distribution: ', tpp, (100-tpp))
print('number of training epochs set to: ', num_epochs)
print('the engine is: ', device)

print()

model = model.to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer_ft = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

model = train_model(checkpointname, model, dataloaders, dataset_sizes, criterion, optimizer_ft, exp_lr_scheduler, device, num_epochs, output)
print('Finished Training')
