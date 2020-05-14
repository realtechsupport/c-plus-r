#!/usr/bin/env python3
# stt.py
# utilities for STT
# Catch+Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
#spring 2020
# tested on ubuntu 18 LTS, kernel 5.3.0
#-------------------------------------------------------------------------------
import sys, os
from av_helper import *
from utilities import *
from stt_helper import *

#-------------------------------------------------------------------------------
def extract_text(app, videofile, language, startsecs, duration, chunk, tconfidence, maxattempts, searchterm, authsource):
    print2screen = True
    #cpath = os.getcwd()
    cpath = app.config['TMP']
    now = strftime("%Y-%m-%d_%H:%M", gmtime())
    videoname = videofile.split('/')[-1] + '_'
    textlog = app.config['TMP'] +'s2tlog_' + videoname + now +'.txt'
    encoding = 'wav'
    path_audioinput = extract_audio_from_video(videofile, encoding)
    audioinput = path_audioinput.split('/')[-1]
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = authsource

    #create the slices
    destination = app.config['TMP']
    starts=[]
    starts = make_slices_from_audio(cpath, videofile, audioinput, startsecs, duration, chunk, destination, onechan=True)

    #transcribe each slice
    afiles=[]
    p, d, files = next(os.walk(destination))
    token = '1ch_16k'
    for file in files:
        if (token in file):
            afiles.append(file)
        else:
            pass

    afiles.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    f_count = len(files)
    j=0
    results=[]
    searchresults=[]
    print('afiles: ', len(afiles)); print('starts: ', len(starts))

    for file in afiles:
        transcript, confidence = transcribe_longrunning_audio(destination+file, language, maxattempts)
        print('transcript length: ', len(transcript))
        #print(transcript, confidence)
        time.sleep(3)
        if (print2screen):
            for i in range (len(transcript)):
                if(confidence[i] >= tconfidence):
                    tr_confidence = '%.4f'%(confidence[i])
                    transcript[i] = transcript[i].lower()   #search is case sensitive
                    message = '... start: ' + str(starts[j]) + ' ... ' + 'text: ' + transcript[i] + ' ... ' + 'confidence: ' + str(tr_confidence)
                    print(i, j, message)

                    write2file(textlog, file + '\n')
                    write2file(textlog, starts[j] + '\n')
                    write2file(textlog, str(confidence[i]) + '\n')
                    write2file(textlog, transcript[i] + '\n\n')
                    results.append(message)

                    if(searchterm != ''):
                        if(searchterm in transcript[i]):
                            searchresults.append(message)

        j=j+1
    #turn this empty until you use it again
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''
    return(results, searchresults)

#-------------------------------------------------------------------------------
def label_images(app, videonamepath, language, authsource, key, maxattempts, nimages, tconfidence):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = authsource
    duration = get_video_length(videonamepath)
    duration_s = hms_to_seconds(duration)
    videopath = (videonamepath.split('.'))[0]

    if(duration_s < 60):
        audiofile_1ch = videopath + '_1ch_16k.wav'
        command = "ffmpeg -i " + videonamepath + " -loglevel panic -y -ab 160k -ac 1 -ar 16000 -vn " + audiofile_1ch
        subprocess.call(command, shell=True)
        transcribe_file_with_word_time_offsets(app, audiofile_1ch, videonamepath, key, language, maxattempts, nimages, tconfidence)

    else:
        print('dividing 60 sec ++ video into segments ...')
        source = videonamepath
        chunksize = 0.75
        location = app.config['TMP']
        nfiles = chunk_large_videofile(source, chunksize, location)
        os.remove(videonamepath)

        path, dirs, files = next(os.walk(location))
        for file in files:
            videoname = (file.split('.'))[0]
            audiofile_1ch = videoname + '_1ch_16k.wav'
            cvideo = os.path.join(location, file)
            caudio_1ch = os.path.join(location, audiofile_1ch)
            command = "ffmpeg -i " + cvideo + " -loglevel panic -y -ab 160k -ac 1 -ar 16000 -vn " + caudio_1ch
            subprocess.call(command, shell=True)
            transcribe_file_with_word_time_offsets(app, caudio_1ch, cvideo, key, language, maxattempts, nimages, tconfidence)

    print('finished label images test')
#-------------------------------------------------------------------------------
