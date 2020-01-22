from wtforms import *
from wtforms.fields import *
from flask_wtf import FlaskForm
from wtforms_components import TimeField
from wtforms.validators import NumberRange, Length

class Downloads(FlaskForm):
    txtout = FileField(label='text output selector ', default='na', validators=[validators.InputRequired()])
    submit = SubmitField('download')

class Allinputs(FlaskForm):
    vid = FileField(label='video selector (.webm /.mp4 only)', default='HELLO WORLD', validators=[validators.InputRequired()])

    s_h = IntegerField(label='start hour (0-99)', default=0, validators=[NumberRange(min=0, max=99), validators.InputRequired()])
    s_m = IntegerField(label='start minute (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    s_s = IntegerField(label='start second (0-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])

    e_h = IntegerField(label='end hour (00-99)', default=0, validators=[NumberRange(min=0, max=99), validators.InputRequired()])
    e_m = IntegerField(label='end minute (00-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])
    e_s = IntegerField(label='end second (00-59)', default=0, validators=[NumberRange(min=0, max=59), validators.InputRequired()])

    chunk = IntegerField(label='chunk length in sec (min 5, max 59)', default=30, validators=[NumberRange(min=5, max=59), validators.InputRequired()])
    conf = FloatField(label='confidence threshold for STT (0.0 - 1.0)', default=0.90, validators=[validators.InputRequired()])
    search = StringField(label='(optional) single search term', default='searchterm', validators=[validators.InputRequired()])
    lang = SelectField('language spoken in video segment', choices =  [('en', 'English'),('fr', 'French'),('id-ID', 'Bahasa Indonesia')], default=('id-ID'), validators=[validators.InputRequired()])
