#!/usr/bin/env python3
# inputs.py
# input classes
# Catch+Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
# jan - may 2020
# tested on ubuntu 18 LTS, kernel 5.3.0
#-------------------------------------------------------------------------------
from wtforms import *
from wtforms.fields import *
from flask_wtf import FlaskForm
from wtforms_components import TimeField
from wtforms.validators import NumberRange, Length


class MakeClassifiers(FlaskForm):
    classifier = SelectField('classifier', choices =  [('alexnet', 'Alexnet'),('vanillanet', 'Vanillanet')], default=('vanillanet'), validators=[validators.InputRequired()])
    testcollection = SelectField('test collection', choices =  [('bali-3', 'bali-3'),('bali-3B', 'bali-3B'), ('bali-3D', 'bali-3D')], default=('bali-3'), validators=[validators.InputRequired()])
    normalization = SelectField('normalize dataset with means from:', choices =  [('bali-26', 'bali-26'),('default', 'detault')], default=('bali-26'), validators=[validators.InputRequired()])
    epochs = IntegerField(label='training epochs (5-50)', default=15, validators=[NumberRange(min=0, max=50), validators.InputRequired()])
    momentum = FloatField(label='convergence control momentum (0.0 - 1.0)', default=0.90, validators=[validators.InputRequired()])
    learning_rate = FloatField(label='learning rate (0.0 - 0.1)', default=0.001, validators=[validators.InputRequired()])
    gamma = FloatField(label='learning rate decay factor gamma (0.0 - 0.5)', default=0.1, validators=[validators.InputRequired()])
    max_images = IntegerField(label='max images per category', default=1000, validators=[NumberRange(min=100, max=5000), validators.InputRequired()])
    training_percentage = FloatField(label='percentage of dataset for training (0.1 - 0.9)', default=0.5, validators=[NumberRange(min=0.1, max=0.9), validators.InputRequired()])
    pretrained = BooleanField('use pretrained network', default=True)

class TestClassifiers(FlaskForm):
    classifier = SelectField('classifier', choices =  [('bali26_resnet152.pth', 'Resnet152 (bali26)'),('bali26_resnext50.pth', 'Resnext50 (bali26)'),('bali26_alexnet.pth', 'Alexnet (bali26)')], default=('bali26_resnet152.pth'), validators=[validators.InputRequired()])
    testcollection = SelectField('test collection', choices =  [('bali26samples', 'bali26'),('tba', 'tba')], default=('bali26samples'), validators=[validators.InputRequired()])

class Checkimagesinputs(FlaskForm):
    ssim_min = IntegerField(label='min structural similarity % (0-99)', default=45, validators=[NumberRange(min=0, max=99), validators.InputRequired()])
    lum_max = IntegerField(label='max luminescence % (100-500)', default=125, validators=[NumberRange(min=0, max=500), validators.InputRequired()])
    lum_min = IntegerField(label='min luminescence % (0-99)', default=75, validators=[NumberRange(min=0, max=5), validators.InputRequired()])

class DownloadInputs(FlaskForm):
    txtout = FileField(label='text output selector ', default='na', validators=[validators.InputRequired()])
    submit = SubmitField('download')

class GetTextinputs(FlaskForm):
    vid = FileField(label='.webm /.mp4 only', default='HELLO WORLD', validators=[validators.InputRequired()])
    s_m = IntegerField(label='start minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    s_s = IntegerField(label='start second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    e_m = IntegerField(label='end minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    e_s = IntegerField(label='end second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    chunk = IntegerField(label='chunk length in sec (min 5, max 59)', default=30, validators=[NumberRange(min=5, max=59), validators.InputRequired()])
    conf = FloatField(label='confidence threshold for STT (0.0 - 1.0)', default=0.90, validators=[validators.InputRequired()])
    search = StringField(label='(optional) single search term', default='searchterm', validators=[validators.InputRequired()])
    auth = FileField(label='key for capture-text (.json)', default='HELLO WORLD')
    lang = SelectField('language spoken in video segment', choices =  [('en-US', 'English'),('fr', 'French'),('id-ID', 'Bahasa Indonesia')], default=('id-ID'), validators=[validators.InputRequired()])

class AnotateInputs(FlaskForm):
    vid = FileField(label='field video', default='HELLO WORLD')
    mic = SelectField(label='microphone', choices =  [('0,0', 'default'),('AT2020', 'AT2020'),('USB Audio', 'USB Audio')], default=('default'), validators=[validators.InputRequired()])
    sa_m = IntegerField(label='start minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    sa_s = IntegerField(label='start second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    ea_m = IntegerField(label='end minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    ea_s = IntegerField(label='end second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])

class PrepareInputs(FlaskForm):
    vid = FileField(label='video', default='')
    chunk = IntegerField(label='chunk size (min)', default=3, validators=[NumberRange(min=0, max=59), validators.InputRequired()])

class VideoLabelInputs(FlaskForm):
    vid = FileField(label='video', default='HELLO WORLD', validators=[validators.InputRequired()])
    framerate = IntegerField(label='framerate (opt b; 1-30)', default=5, validators=[NumberRange(min=1, max=30), validators.InputRequired()])
    folder = StringField(label='foldername (opt b)', default='category', validators=[validators.InputRequired()])
    label = StringField(label='keyterm (opt a)', default='searchterm', validators=[validators.InputRequired()])
    nimages = IntegerField(label='images / utterance (opt a; 1-30)', default=20, validators=[NumberRange(min=1, max=30), validators.InputRequired()])
    conf = FloatField(label='confidence threshold for STT (opt a; 0.0 - 1.0)', default=0.90, validators=[validators.InputRequired()])
    auth = FileField(label='key for capture-text (.json; opt a)', default='HELLO WORLD')
    lang = SelectField('language in video segment (opt a)', choices =  [('en-US', 'English'),('fr', 'French'),('id-ID', 'Bahasa Indonesia')], default=('id-ID'), validators=[validators.InputRequired()])
