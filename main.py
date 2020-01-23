
#!/usr/bin/env python3
# main.py
# jan 2020
# built requirements.txt, fails to build on GCP
# https://stackoverflow.com/questions/55474474/minimalistic-app-getting-oserror-errno-12-cannot-allocate-memory-on-deploy
# https://issuetracker.google.com/issues/129913216
# removed call to torch, torchvision > build successful
#------------------------------------------------------------------------------
import sys, os, time, shutil, glob
from flask import Flask, flash, current_app, send_file, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from stt import *
from inputs import *
from av_helper import *
from utilities import *

#make directories tmp, audiosegments, results ---------------------------------
cwd = os.getcwd()
s_dir = cwd + '/static/'

#-------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['ROOT'] = cwd
app.config['STATIC'] = s_dir

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

#------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():

    formats = ('*.webm', '*.wav', '*.mp4', '*.MP4', '*.txt', '*.zip')
    locations = ('STATIC', 'ROOT')
    removefiles(app, formats, locations)
    flash("...deleting data files....", category='notice')

    template = 'index.html'
    return render_template(template)

#------------------------------------------------------------------------------
@app.route('/inputview', methods=['GET', 'POST'])
def inputview():
    form = Allinputs()
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

            destination = os.path.join(app.config['ROOT'], filename)
            shutil.copyfile(revsource, destination)

            session['s_filename'] = filename

            #get the other inputs ....start and end times
            s_h = form.s_h.data; s_m = form.s_m.data; s_s = form.s_s.data
            e_h = form.e_h.data; e_m = form.e_m.data; e_s = form.e_s.data

            start_time = s_s + 60*s_m + 3600*s_h
            end_time = e_s + 60*e_m + 3600*e_h
            duration = end_time - start_time
            start = seconds_to_hms(start_time); end = seconds_to_hms(end_time)

            if('searchterm' in form.search.data):
                searchterm = ''
            else:
                searchterm = form.search.data

            os.chdir(app.config['ROOT'])
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
    form = Downloads()
    template = 'outputview.html'
    log = ''

    s_results = session.get('s_results', None)
    s_searchresults = session.get('s_searchresults', None)
    s_filename = session.get('s_filename', None)

    if (request.method == 'POST'):
        print('inside the download option..')
        template = 'index.html'
        if("download" in request.form):
            #resultspath = os.path.join(current_app.root_path, app.config['ROOT'])
            resultspath = app.config['ROOT'] + '/'
            for name in glob.glob(resultspath + '*s2tlog*'):
                log = name

            if(log):
                return send_file(log, as_attachment=True)
            else:
                print('no results to download...')

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
if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=8080, debug=True)
    app.run()
#-------------------------------------------------------------------------------
