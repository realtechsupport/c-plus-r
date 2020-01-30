
#!/usr/bin/env python3
# main.py
# jan 2020
# built requirements.txt, fails to build on GCP
# https://stackoverflow.com/questions/55474474/minimalistic-app-getting-oserror-errno-12-cannot-allocate-memory-on-deploy
# https://issuetracker.google.com/issues/129913216
# removed call to torch, torchvision > build successful
#------------------------------------------------------------------------------
import sys, os, time, shutil, glob
import eventlet, json
import random, threading, webbrowser
from flask import Flask, flash, current_app, send_file, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from stt import *
from av_helper import *
from inputs import *
from utilities import *

#make directories tmp, audiosegments, results ---------------------------------
cwd = os.getcwd()
t_dir = cwd + '/tmp/'
a_dir = cwd + '/anotate/'
s_dir = cwd + '/static/'
i_dir = cwd + '/images/'

if not os.path.exists(t_dir):
    os.makedirs(t_dir)
if not os.path.exists(a_dir):
    os.makedirs(a_dir)
if not os.path.exists(i_dir):
    os.makedirs(i_dir)
#-------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['TMP'] = t_dir
app.config['STATIC'] = s_dir
app.config['ANOTATE'] = a_dir
app.config['IMAGES'] = i_dir
app.config['MIC'] = 'AT2020'          #'UC02' 'AT2020'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

socketio = SocketIO(app, async_mode="eventlet")
#------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():

    formats = ('*.webm', '*.wav', '*.mp4', '*.MP4', '*.txt', '*.zip', '*.prof')
    locations = ('STATIC', 'TMP', 'ANOTATE')
    removefiles(app, formats, locations)
    flash("...deleting data files....", category='notice')
    template = 'index.html'
    return render_template(template)

#------------------------------------------------------------------------------
@app.route('/inputview', methods=['GET', 'POST'])
def inputview():
    form = GetTextinputs()
    template = 'inputview.html'
    results = []
    searchresults = []
    revsource = ''
    filename = ''
    upl = False

    if (request.method == 'POST'):
        if("delete" in request.form):
            print('deleting existing data...')
            removefiles(app, patterns, locations)
        #-----------------------------------------------------------------------
        elif("view" in request.form):
            temp = session.get('s_filename', None)
            if(temp == ''):
                s_filename = ''
            else:
                s_filename = temp

            file = request.files['vid']
            filename = secure_filename(file.filename).lower()
            revsource = os.path.join(app.config['STATIC'], filename)

            if(s_filename == None):
                print('no file yet..')
                pass
            elif((s_filename.split('.')[0]) == filename.split('.')[0]):
                m = os.path.join(app.config['STATIC'], s_filename)
                if(os.path.isfile(m)):
                    upl = True;
                    print('file already uploaded')

            if(upl == False):
                print('.... uploading .....')
                file.save(revsource)

                videoformat = (filename.split('.')[1]).lower()
                print('this is the videoformat: ', videoformat)

                if(videoformat == 'mp4'):
                    convert_mp4_to_webm(revsource)
                    filename = filename.split('.')[0] +  '.webm'
                    #print('conversion from .mp4 to .webm finished.....')

            session['s_filename'] = filename

        #-----------------------------------------------------------------------
        elif("capture" in request.form):
            temp = session.get('s_filename', None)
            if(temp == ''):
                s_filename = ''
            else:
                s_filename = temp

            file = request.files['vid']
            filename = secure_filename(file.filename).lower()
            revsource = os.path.join(app.config['STATIC'], filename)

            if(s_filename == None):
                print('no file yet..')
                pass
            elif((s_filename.split('.')[0]) == filename.split('.')[0]):
                m = os.path.join(app.config['STATIC'], s_filename)
                if(os.path.isfile(m)):
                    upl = True;
                    print('file already uploaded')

            if(upl == False):
                print('.... uploading .....')
                file.save(revsource)

                videoformat = (filename.split('.')[1]).lower()
                print('this is the videoformat: ', videoformat)

                if(videoformat == 'mp4'):
                    convert_mp4_to_webm(revsource)
                    filename = filename.split('.')[0] +  '.webm'
                    #print('conversion from .mp4 to .webm finished.....')

            destination = os.path.join(app.config['TMP'], filename)
            shutil.copyfile(revsource, destination)

            session['s_filename'] = filename

            #get the other inputs ....start and end times minutes / seconds only
            s_h = 0
            s_m = form.s_m.data; s_s = form.s_s.data
            e_h = 0
            e_m = form.e_m.data; e_s = form.e_s.data

            start_time = s_s + 60*s_m + 3600*s_h
            end_time = e_s + 60*e_m + 3600*e_h
            duration = end_time - start_time
            start = seconds_to_hms(start_time); end = seconds_to_hms(end_time)

            if('searchterm' in form.search.data):
                searchterm = ''
            else:
                searchterm = form.search.data

            os.chdir(app.config['TMP'])
            maxattempts = 5
            results, searchresults = extract_text(app, destination, form.lang.data, start_time, duration, form.chunk.data, form.conf.data, maxattempts, searchterm)
            #session variables limited to 4kb !!
            session['s_results'] = results; session['s_searchresults'] = searchresults

            for line in results:
                print (line)

            template = 'outputview.html'
            return redirect(url_for('outputview'))

    else:
        results = None
        searchresults = None

    return(render_template(template, form=form, result=results, sresult=searchresults, showvideo=filename))

#-------------------------------------------------------------------------------
@app.route('/outputview', methods=['GET', 'POST'])
def outputview():
    form = DownloadInputs()
    template = 'outputview.html'

    s_results = session.get('s_results', None)
    s_searchresults = session.get('s_searchresults', None)
    s_filename = session.get('s_filename', None)

    if (request.method == 'POST'):
        print('inside the download option..')
        template = 'index.html'
        if("download" in request.form):
            resultspath = os.path.join(current_app.root_path, app.config['TMP'])
            #should only be one file...
            for name in glob.glob(resultspath + '*s2tlog*'):
                log = name

            return send_file(log, as_attachment=True)

    return render_template(template, form=form, result=s_results, sresult=s_searchresults, showvideo=s_filename)

#-------------------------------------------------------------------------------
@app.route('/labelimagesview')
def labelimagesview():
    template = 'labelimagesview.html'
    return render_template(template)

#-------------------------------------------------------------------------------
@app.route('/infoview')
def infoview():
    template = 'infoview.html'
    return render_template(template)

#-------------------------------------------------------------------------------
@app.route('/audioanotate', methods=['GET', 'POST'])
def audioanotate():
    form = AnotateInputs()
    template = 'audioanotate.html'
    filename = ''
    upl = False

    if (request.method == 'POST'):
        if("load" in request.form):
            print('in recording section')

            mic = form.mic.data
            file = request.files['vid']

            filename = secure_filename(file.filename).lower()
            print(filename)
            revsource = os.path.join(app.config['STATIC'], filename)
            ansource = os.path.join(app.config['ANOTATE'], filename)
            file.save(revsource)
            time.sleep(1)
            copyfile(revsource, ansource)

            cardn, devicen = mic_info(mic)
            session['cardn'] = cardn
            session['devicen'] = devicen
            session['s_filename'] = filename


    if (request.method == 'POST'):
        if("segment" in request.form):
            print('in SEGMENT section')
            sa_h = 0; sa_m = form.sa_m.data; sa_s = form.sa_s.data
            ea_h = 0; ea_m = form.ea_m.data; ea_s = form.ea_s.data

            start_cut = sa_s + 60*sa_m + 3600*sa_h
            end_cut = ea_s + 60*ea_m + 3600*ea_h
            duration = end_cut - start_cut
            session['start_cut'] = start_cut
            session['end_cut'] = end_cut

            video = session.get('s_filename')
            cut_video = get_segment(video, start_cut, end_cut)

            source = os.path.join(app.config['ANOTATE'], cut_video)
            destination = os.path.join(app.config['STATIC'], cut_video)
            copyfile(source, destination)
            filename = cut_video
            session['s_filename'] = filename

            #print('Copied to annotate and static: SEGMENT:', start_cut, end_cut)

    return render_template(template, form=form, showvideo=filename)

#-------------------------------------------------------------------------------

@socketio.on('event')
def handle_my_custom_namespace_event(jsondata):
    print('received json: ' + str(jsondata))

@socketio.on('response')
def handle_response(jsondata):

    card =  session.get('cardn')
    device = session.get('devicen')
    video = session.get('s_filename')
    st = session.get('start_cut')
    end = session.get('end_cut')
    #get data from the user
    (k,v), = jsondata.items()

    os.chdir(app.config['ANOTATE'])

    if(k == 'start'):
        if (session.get('nrecordings') == None):
            session['nrecordings'] = 1
        else:
            print('KEY, VALUE: ', k,v)
            duration = get_video_length(video)
            print('actual video duration: ', duration)
            newaudio = 'naudio_' + video.split('.')[0] + '.wav'
            voiceover_recording(duration, card, device, newaudio)
            #remove noise if necessary
            #crecording = cleanrecording(output)
            combination = 'voiceover_' + str(st) + '-' + str(end) + '_' + video.split('.')[0] + '.mkv'
            result = ''
            result = combine_recordingvideo(newaudio, video, combination)
            print(result)
            f

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    port = 5000
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    socketio.run(app, port=port, debug=False)

#-------------------------------------------------------------------------------
