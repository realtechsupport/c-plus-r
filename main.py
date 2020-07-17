#!/usr/bin/env python3
# main.py
# Catch & Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
# spring 2020
# tested on ubuntu 18 LTS, kernel 5.3.0; Mac OS Catalina
#-------------------------------------------------------------------------------
#1. start virtual env
#2. launch the program
# python3 main.py ubuntu firefox debug, or
# python3 main.py mac chromium no-debug\' for example.

# OS: ubuntu or mac. Browsers: chromium or firefox.
# issue: can not get flask-caching to work properly
# solution: Classic Cache Killer for Chrome; after install check options (right click, enable at start)
#------------------------------------------------------------------------------
import sys, os, time, shutil, glob
import eventlet, json
import random, threading, webbrowser
from flask import Flask, flash, current_app, send_file, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from stt import *
from av_helper import *
from inputs import *
from utilities import *
from similarities import *
from pyt_utilities import *

app = Flask(__name__, template_folder="templates")
cwd = app.root_path

t_dir = cwd + '/tmp/';          a_dir = cwd + '/anotate/'
s_dir = cwd + '/static/';       i_dir = cwd + '/images/'
m_dir = cwd + '/models/';       c_dir = cwd + '/collection/'
r_dir = cwd + '/results/';      ar_dir = cwd + '/archive/'
f_dir = cwd + '/find/';         cl_dir = cwd + '/classify/'
te_dir = cwd + '/tests/'

dirs = [t_dir, a_dir, s_dir, i_dir, m_dir, c_dir, r_dir, ar_dir, f_dir, cl_dir, te_dir]
for dir in dirs:
    if not os.path.exists(dir):
        os.makedirs(dir)

app.config['SECRET_KEY'] = 'you-will-not-guess'
app.config['TMP'] = t_dir;      app.config['STATIC'] = s_dir
app.config['ANOTATE'] = a_dir;  app.config['IMAGES'] = i_dir
app.config['MODELS'] = m_dir;   app.config['COLLECTION'] = c_dir
app.config['RESULTS'] = r_dir;  app.config['FIND'] = f_dir
app.config['ARCHIVE'] = ar_dir; app.config['CLASSIFY'] = cl_dir
app.config['TESTS'] = te_dir

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

socketio = SocketIO(app, async_mode="eventlet")
#------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    session.clear()
    formats = ('*.json', '*.webm', '*.wav', '*.mp4', '*.MP4', '*.txt', '*.zip', '*.prof', '*.mkv', '*.jpg', '*.csv', '*.pth')
    locations = ('STATIC', 'ANOTATE', 'TMP', 'IMAGES', 'RESULTS')
    exception = 'voiceover'

    try:
        removefiles(app, formats, locations, exception)
    except:
        pass

    if not os.path.exists(i_dir):
        os.makedirs(i_dir)

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
        if("view" in request.form):
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

            session['s_filename'] = filename
        #------------------------------------------
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

            destination = os.path.join(app.config['TMP'], filename)
            shutil.copyfile(revsource, destination)

            session['s_filename'] = filename
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

            try:
                auth_file = request.files['auth']
                auth_filename = secure_filename(auth_file.filename).lower()
                authsource = os.path.join(app.config['STATIC'], auth_filename)
                auth_file.save(authsource)
            except:
                print('no credential file selected - cannot capture text without a valid [.json] credential ')
                return redirect(url_for('inputview'))

            #now get the text from the set segment
            os.chdir(app.config['TMP'])
            maxattempts = 5
            results, searchresults = extract_text(app, destination, form.lang.data, start_time, duration, form.chunk.data, form.conf.data, maxattempts, searchterm, authsource)
            print('\n finished extracting text from video..\n')
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
            for name in glob.glob(resultspath + '*s2tlog*'):
                log = name

            return send_file(log, as_attachment=True)

    return render_template(template, form=form, result=s_results, sresult=s_searchresults, showvideo=s_filename)

#-------------------------------------------------------------------------------
@app.route('/checkimagesview',  methods=['GET', 'POST'])
def checkimagesview():
    form = Checkimagesinputs()
    current_video = ''
    category = ''
    dfiles = ''
    key = ''
    wordcollection = []
    images = ''
    template = 'checkimagesview.html'

    key = session.get('s_key', None)
    wordcollection = session.get('s_wordcollection', None)
    videoname = session.get('s_videoname', None)
    current_video = videoname.split('/')[-1]
    category = session.get('s_category', None)

    if(len(wordcollection) == 0):
        print('\n\nNO MATHCES ... try again\n\n')
        return render_template(template, form=form, category = key, videoname = current_video, images = images)

    #use the first of the actually detected words when there are more than one
    if(key != ''):
        if(len(wordcollection) > 0):
            key = wordcollection[0]

    if(key == ''):
        images = os.listdir(app.config['IMAGES'] + category)
    else:
        images = os.listdir(app.config['IMAGES'] + key)


    lastentry_d = 0; firstentry_s = 0

    if (request.method == 'POST'):
        ssim_min = form.ssim_min.data;
        lum_max = form.lum_max.data;
        lum_min = form.lum_min.data;

        if("add" in request.form):
            if(key == ''):
                destination = os.path.join(app.config['COLLECTION'], category)
            else:
                destination = os.path.join(app.config['COLLECTION'], key)

            if not os.path.exists(destination):
                os.makedirs(destination)

            #find the highest number in the destination and the lowest in the source
            dfiles = glob.glob(destination + '/*.jpg')
            if(key == ''):
                source = os.path.join(app.config['IMAGES'], category)
            else:
                source = os.path.join(app.config['IMAGES'], key)

            sfiles = glob.glob(source + '/*.jpg')

            try:
                dfiles = [i.split('/')[-1] for i in dfiles]
                dfiles = [i.split('.')[0] for i in dfiles]
                dfiles = sorted([int(i) for i in dfiles])
                lastentry_d = dfiles[-1]
            except:
                lastentry_d = 0

            try:
                ssfiles = [i.split('/')[-1] for i in sfiles]
                ssfiles = [i.split('.')[0] for i in ssfiles]
                ssfiles = sorted([int(i) for i in ssfiles])
                firstentry_s = ssfiles[0]
            except:
                firstentry_s = 0

            if(firstentry_s < lastentry_d):
                print('first entry source smaller than in last in destination...renaming source images')
                rename_all(source, lastentry_d)

            #copy the files
            rfiles = glob.glob(source + '/*.jpg')
            rfiles = sorted(rfiles)
            for file in rfiles:
                shutil.copy(file, destination)
            print('COPIED images to collection')

        elif("divergent" in request.form):
            print('removing fuzzy, over and underexposed images...')
            try:
                images2remove = session.get('s_images2remove', None)
                imlist = json.loads(images2remove)
                if(key == ''):
                    im_loc = os.path.join(app.config['IMAGES'], category) + '/'
                else:
                    im_loc = os.path.join(app.config['IMAGES'], key) + '/'

                im_ref =  imlist[-1]
                nbad = remove_fuzzy_over_under_exposed(im_ref, im_loc, images, ssim_min, lum_max, lum_min)
                print('removed ' +  str(nbad) + ' images...')
            except:
                print('no images selected to create reference...')

        elif("delete" in request.form):
            print('removing highlighted images...')
            try:
                images2remove = session.get('s_images2remove', None)
                imlist = json.loads(images2remove)
                for im in imlist:
                    if(key == ''):
                        im_s = os.path.join(app.config['IMAGES'], category, im)

                    else:
                        im_s = os.path.join(app.config['IMAGES'], key, im)

                    print(im_s)
                    try:
                        os.remove(im_s)
                    except:
                        print('image already removed')
            except:
                print('no images selected for removal...')

        elif("remove" in request.form):
            try:
                print('delelting the entire collection !')
                shutil.rmtree(app.config['COLLECTION'])
            except:
                pass
            if not os.path.exists(app.config['COLLECTION']):
                os.makedirs(app.config['COLLECTION'])

        elif("archive" in request.form):
            #shutil.make_archive(app.config['COLLECTION'], 'zip', app.config['COLLECTION'])... works from commandline...
            zfile = 'collection.zip'; timezone = 'America/New_York'
            stamped_zfile = create_timestamp(zfile, timezone)
            zipit(app.config['COLLECTION'], stamped_zfile)
            source = os.path.join(app.config['COLLECTION'], stamped_zfile)
            destination = os.path.join(app.config['ARCHIVE'], stamped_zfile)
            shutil.move(source, destination)


        elif("context" in request.form):
            pass

        elif("share" in request.form):
            pass

        #left click on mouse collects the images
        else:
            try:
                imagenames = request.form['data']
                session['s_images2remove'] = imagenames
            except ValueError:
                pass

    if(key == ''):
        return render_template(template, form=form, category = category, videoname = current_video, images = images)
    else:
        return render_template(template, form=form, category = key, videoname = current_video, images = images)

#-------------------------------------------------------------------------------
@app.route('/checkimagesview/<filename>')
def send_image(filename):
    category = session.get('s_category', None)
    key = session.get('s_key', None)
    wordcollection = []

    #------------new
    wordcollection = session.get('s_wordcollection', None)
    print('HERE wordcollection: ', wordcollection)
    #use the first of the detected words, when there are more than one
    if(key != ''):
        if(len(wordcollection) > 0):
            key = wordcollection[0]
    print('Revised key: ', key)

    if(key == ''):
        location = 'images/' + category
    else:
        location = 'images/' + key

    return send_from_directory(location, filename)

#-------------------------------------------------------------------------------
@app.route('/labelimagesview', methods=['GET', 'POST'])
def labelimagesview():
    form = VideoLabelInputs()
    revsource = ''
    videoname = ''
    file = ''
    category = ''
    key = ''
    wordcollection = []
    template = 'labelimagesview.html'

    if (request.method == 'POST'):
        if("load" in request.form):
            file = request.files['vid']
            videoname = secure_filename(file.filename).lower()
            revsource = os.path.join(app.config['STATIC'], videoname)
            file.save(revsource)

        elif("bulk" in request.form):
            print('...labelling bulk category')
            framerate = form.framerate.data
            file = request.files['vid']
            videoname= secure_filename(file.filename)
            videonamepath = os.path.join(app.config['TMP'], videoname)
            file.save(videonamepath)
            category = form.folder.data
            savepath = os.path.join(app.config['IMAGES'],  category) + '/'
            create_images_from_video(savepath, category, videonamepath, framerate)
            print('FINISHED bulk saving')

        elif("audio" in request.form):
            print('...labelling with keys')
            key = form.label.data
            language = form.lang.data

            try:
                file = request.files['auth']
                auth = secure_filename(file.filename)
                authsource = os.path.join(app.config['STATIC'], auth)
                file.save(authsource)
            except:
                print('no credential file selected - cannot capture text without a valid [.json] credential ')
                return redirect(url_for('labelimagesview'))

            file = request.files['vid']
            videoname= secure_filename(file.filename)
            videonamepath = os.path.join(app.config['TMP'], videoname)
            file.save(videonamepath)

            nimages = form.nimages.data
            tconfidence = form.conf.data
            maxattempts = 5
            wordcollection = label_images(app, videonamepath, language, authsource, key, maxattempts, nimages, tconfidence)
            print('FINISHED labelling by keys')

    session['s_videoname'] = videoname
    session['s_category'] = category
    session['s_key'] = key
    session['s_wordcollection'] = wordcollection

    return render_template(template, form=form, showvideo=videoname)

#-------------------------------------------------------------------------------
@app.route('/testclassifiers', methods=['GET', 'POST'])
def testclassifiers():
    form = TestClassifiers()
    choice = ''; input = ''; images = ''; files = ''; c_classifier = ''
    result = ''; moreresults = ''; tp_vals = []
    template = 'testclassifiers.html'

    if (request.method == 'POST'):
        testcollection = form.testcollection.data
        print('\n\ntest collection is: ', testcollection)
        location = os.path.join(app.config['FIND'], testcollection)
        zfile = os.path.join(app.config['FIND'], testcollection) + '.zip'
        try:
            path, dirs, files = next(os.walk(location))
        except:
            pass

        if(len(files) == 0):
            if(testcollection == 'bali26samples'):
                archive = bali26_samples_zip
                print('downloading the samples...')
                wget.download(archive, zfile)
                shutil.unpack_archive(zfile, app.config['FIND'], 'zip')
                os.remove(zfile)
            else:
                #here other archives
                archive = bali26_samples_zip

        images = os.listdir(location)

        if("display" in request.form):
            session['s_testcollection'] = testcollection
            #display = True; session['s_choices'] = ''
        elif(("classify" in request.form) and (session.get('s_choices', None) != '' )):
            classifier = form.classifier.data
            session['s_testcollection'] = testcollection

            if(testcollection != 'bali26samples'):
                print('\nother collections not yet ready...\n\n')
                return redirect(url_for('testclassifiers'))


            if(testcollection == 'bali26samples'):
                class_names = bali26_class_names

                if(classifier == 'bali26_resnet152'):
                    archive = bali26_resnet152
                elif(classifier == 'bali26_resnet152_np'):
                    archive = bali26_resnet152_notpretrained

                elif(classifier == 'bali26_resnext50'):
                    archive = bali26_resnext50
                elif(classifier == 'bali26_resnext50_np'):
                    archive = bali26_resnext50_notpretrained

                elif(classifier == 'bali26_alexnet'):
                    archive = bali26_alexnet
                elif(classifier == 'bali26_alexnet_np'):
                    archive = bali26_alexnet_notpretrained

                else:
                    archive = bali26_alexnet

                classifier = classifier + '.pth'
                print('selected classifier: ', classifier)

                path, dirs, files = next(os.walk(app.config['MODELS']))
                if(classifier in files):
                    print('already have the matching classifier...\n')
                    pass
                else:
                    print('getting the matching classifier...\n')
                    modelname = archive.split('/')[-1]
                    wget.download(archive, (os.path.join(app.config['MODELS'], modelname)))

            try:
                tchoices = session.get('s_choices', None)
                choice = json.loads(tchoices)
                image_path = os.path.join(app.config['FIND'],  testcollection, choice)
                pclassifier = os.path.join(app.config['MODELS'], classifier)
                processor='cpu'; tk=3; threshold=90;
                model = load_checkpoint(pclassifier, processor)
                predictions, percentage, outcategory = predict_image(image_path, model, predict_transform, class_names, tk, processor)
                tp_indeces = predictions[1].tolist()[0]
                for k in tp_indeces:
                    tp_vals.append(class_names[k])

                input = 'selected image: ' + choice
                c_classifier = 'selected classifier: ' + classifier
                result = 'best prediction: ' + outcategory + ' (with confidence level ' + percentage + '%)'
                moreresults = 'top three predictions: ' + str(tp_vals)

            except:
                print('exception encountered ... click display images, pick an image (with left mouse button) before you classify ... ')
                return redirect(url_for('testclassifiers'))

        elif("context" in request.form):
            images = ''

        #left click on mouse collects the images
        else:
            try:
                imagenames = request.form['data']
                session['s_choices'] = imagenames
            except:
                print('no image selected to classify')
                pass

    return render_template(template, form=form, images=images, result=result, moreresults=moreresults, classifier=c_classifier, input=input)

#-------------------------------------------------------------------------------
@app.route('/testclassifiers/<filename>')
def classify_image(filename):
    testcollection = session.get('s_testcollection', None)
    location = os.path.join(app.config['FIND'], testcollection)
    return send_from_directory(location, filename)

#-------------------------------------------------------------------------------
@app.route('/showinfoview')
def showinfoview():
    template = 'showinfoview.html'
    return render_template(template)

#-------------------------------------------------------------------------------
@app.route('/prepareview', methods=['GET', 'POST'])
def prepareview():
    form = PrepareInputs()
    template = 'prepareview.html'
    chunkresult = '...'
    filename = ''

    if (request.method == 'POST'):
        if("samples" in request.form):
            zfile = os.path.join(app.config['TESTS'], 'tests.zip')
            lzfile = 'tests.zip'
            path, dirs, files = next(os.walk(app.config['TESTS']))
            if(lzfile in files):
                print('already downloaded the sample data..')
                pass
            else:
                try:
                    wget.download(tests_zip, zfile)
                    shutil.unpack_archive(zfile, app.config['TESTS'], 'zip')
                except:
                    print('can not get the samples...')
                    return redirect(url_for('prepareview'))

        elif("chunk" in request.form):
            chunksize = form.chunk.data
            try:
                file = request.files['vid']
                filename = secure_filename(file.filename).lower()
                #print(filename, chunksize)
                destination = os.path.join(app.config['TMP'], filename)
                file.save(destination)
                location = app.config['TMP']
                nfiles = chunk_large_videofile(destination, chunksize, location)
                chunkresult = 'result: ' + str(nfiles) + ' files of max ' + str(chunksize) + ' min...'
            except:
                print('Something went wrong...file less than 1 min long? No file chosen? Supported fromats are .webm and .mp4 only. Try again...')
                return redirect(url_for('prepareview'))

        else:
            print('SOMETHING ELSE')

    return render_template(template, form=form, result=chunkresult)

#-------------------------------------------------------------------------------
@app.route('/audioanotate', methods=['GET', 'POST'])
def audioanotate():
    form = AnotateInputs()
    template = 'audioanotate.html'
    filename = ''
    cut_video = ''
    session['s_filename_w'] = ''
    upl = False

    if (request.method == 'POST'):
        if("load" in request.form):
            print('in recording section')
            mic = form.mic.data
            try:
                file = request.files['vid']
                filename = secure_filename(file.filename).lower()
                print(filename)
                revsource = os.path.join(app.config['STATIC'], filename)
                ansource = os.path.join(app.config['ANOTATE'], filename)
                file.save(revsource)
                time.sleep(1)
                copyfile(revsource, ansource)
            except:
                print('please select a video...')
                return redirect(url_for('audioanotate'))

            cardn, devicen = mic_info(mic)
            print('mic info: ', cardn, devicen)
            session['cardn'] = cardn
            session['devicen'] = devicen
            session['s_filename'] = filename

        elif("remove" in request.form):
            print('removing old voice-over assets')
            tpatterns = ('*.webm', '*.wav', '*.mp4', '*.MP4', '*.mkv')
            tlocations = ('STATIC', 'ANOTATE', 'TMP')
            texception = 'nothing'
            try:
                removefiles(app, tpatterns, tlocations, texception)
            except:
                return redirect(url_for('audioanotate'))

        elif("check" in request.form):
            print('recording 3 seconds of audio for system check... ')
            mic = form.mic.data
            cardn, devicen = mic_info(mic)
            session['cardn'] = cardn
            session['devicen'] = devicen
            dur = 3;
            output = os.path.join(app.config['TMP'], 'audiocheck.wav')
            record_and_playback(dur, cardn, devicen, output)
            return redirect(url_for('audioanotate'))

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
            try:
                cut_video = get_segment(video, start_cut, end_cut)
            except:
                print('something wrong - did you set start and end time correctly?')
                return redirect(url_for('audioanotate'))

            session['s_filename_w'] = cut_video
            session['s_filename'] = cut_video

            videoformat = (video.split('.')[1]).lower()
            if(videoformat == 'mp4'):
                cut_video = convert_mp4_to_webm_rt(cut_video)
                print('conversion of segment from .mp4 to .webm finished.....')
                session['s_filename'] = cut_video

            source = os.path.join(app.config['ANOTATE'], cut_video)
            destination = os.path.join(app.config['STATIC'], cut_video)
            copyfile(source, destination)
            filename = cut_video
            print('voiceover file now in anotate folder.')

    return render_template(template, form=form, showvideo=filename)

#-------------------------------------------------------------------------------
@socketio.on('event')
def handle_my_custom_namespace_event(jsondata):
    print('received json: ' + str(jsondata))

@socketio.on('response')
def handle_response(jsondata):

    card =  session.get('cardn')
    device = session.get('devicen')
    vid_display = session.get('s_filename')
    video = session.get('s_filename_w')
    #print('In the handle response... the display video is now: ', vid_display)

    st = session.get('start_cut')
    end = session.get('end_cut')
    #get data from the user
    (k,v), = jsondata.items()

    os.chdir(app.config['ANOTATE'])

    if(k == 'start'):
        if (session.get('nrecordings') == None):
            session['nrecordings'] = 1
        else:
            #print('KEY, VALUE: ', k,v)
            duration = get_video_length(video)
            print('actual video duration: ', duration)
            newaudio = 'naudio_' + video.split('.')[0] + '.wav'
            voiceover_recording(duration, card, device, newaudio)

            #remove noise if necessary ...crecording = cleanrecording(output)
            vformat = video.split('.')[1]
            if (vformat == 'mp4'):
                updated_vformat = '.mp4'
            else:
                updated_vformat = '.mkv'

            combination = 'voiceover_' + str(st) + '-' + str(end) + '_' + video.split('.')[0] + updated_vformat
            result = combine_recordingvideo(newaudio, video, combination)

            print(result)
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    if(len(sys.argv) < 3):
        print('\nplease provide OS, browser and dubug choice when you start the program.')
        print('\'python3 main.py ubuntu firefox debug\', or \'python3 main.py mac chromium no-debug\' for example.\n')
        print('OS: Ubuntu or MAC. Ubuntu browsers: chromium or firefox; MAC only chrome: \'python3 main.py mac chrome no-debug\' \n')

        sys.exit(2)
    else:
        try:
            osy = sys.argv[1]
            browser = sys.argv[2]
            debug_mode = sys.argv[3]
            print('\n> operating system: ', osy)
            print('> browser: ', browser)
            print('> mode: ', debug_mode)
        except:
            print('... using default ubuntu and chromium in non-debug mode ...')
            osy = 'ubuntu'
            browser = 'chromium-browser'
            debug_mode = 'debug'

    port = 5000
    url = "http://127.0.0.1:{0}".format(port)

    #Two browsers supported in ubuntu; only one (Chrome) in macOS
    if('firefox' in browser):
        browser = 'firefox'
    else:
        browser = 'chromium-browser'


    if('ubuntu' in osy):
        threading.Timer(1.25, lambda: webbrowser.get(browser).open(url) ).start()
    else:
        #launch Chrome on macOS
        threading.Timer(1.25, lambda: webbrowser.get('open -a /Applications/Google\ Chrome.app %s').open(url)).start()
        #Chromium, if installed...
        #threading.Timer(1.25, lambda: webbrowser.get('open -a /Applications/Chromium.app %s').open(url)).start()

    if(debug_mode == 'debug'):
        socketio.run(app, port=port, debug=True)
    else:
        socketio.run(app, port=port, debug=False)
#-------------------------------------------------------------------------------
