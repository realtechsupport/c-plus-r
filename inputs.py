from wtforms import *
from wtforms.fields import *
from flask_wtf import FlaskForm
from wtforms_components import TimeField
from wtforms.validators import NumberRange, Length

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
    lang = SelectField('language spoken in video segment', choices =  [('en', 'English'),('fr', 'French'),('id-ID', 'Bahasa Indonesia')], default=('id-ID'), validators=[validators.InputRequired()])


class AnotateInputs(FlaskForm):
    #vid = FileField(label='select field video', default='HELLO WORLD', validators=[validators.InputRequired()])
    vid = FileField(label='select field video', default='HELLO WORLD')
    mic = SelectField(label='select microphone', choices =  [('0,0', 'default'),('AT2020', 'AT2020'),('UC02', 'UC02')], default=('UC02'), validators=[validators.InputRequired()])
    sa_m = IntegerField(label='start minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    sa_s = IntegerField(label='start second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    ea_m = IntegerField(label='end minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    ea_s = IntegerField(label='end second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
