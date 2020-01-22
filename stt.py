#!/usr/bin/env python3
#stt.py
#utilities for STT
# jan 2020
import sys, os
from av_helper import *
from stt_helper import *

#-------------------------------------------------------------------------------
def extract_text(app, videofile, language, startsecs, duration, chunk, tconfidence, maxattempts, searchterm):
    #print('this is the input data: ', videofile, language, startsecs, duration, chunk, tconfidence, searchterm)
    print2db = False
    print2screen = True
    cpath = os.getcwd()
    now = strftime("%Y-%m-%d_%H:%M", gmtime())

    videoname = videofile.split('/')[-1] + '_'
    #textlog = app.config['ROOT'] +'s2tlog_' + videoname + now +'.txt'
    textlog = 's2tlog_' + videoname + now +'.txt'

    encoding = 'wav'
    path_audioinput = extract_audio_from_video(videofile, encoding)
    audioinput = path_audioinput.split('/')[-1]

    #make sure the speech API is enabled and you have the correct json file
    googcreds = app.config['STATIC'] + 'googcreds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = googcreds

    #create the slices
    destination = app.config['ROOT'] + '/'

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

    if(print2db):
        databasename = videoinput.split('.')[0] + '.db'
        print(databasename)
        connection = create_connection(path, databasename)
        create_table(connection) # if it exists, do nothing

    j=0
    results=[]
    searchresults=[]

    for file in afiles:
        transcript, confidence = transcribe_longrunning_audio(destination+file, language, maxattempts)

        print('transcript length: ', len(transcript))
        #too many requests?
        time.sleep(3)
        if (print2screen):
            for i in range (len(transcript)):
                if(confidence[i] >= tconfidence):
                    tr_confidence = '%.4f'%(confidence[i])
                    message = '... start: ' + str(starts[j]) + ' ... ' + 'text: ' + transcript[i] + ' ... ' + 'confidence: ' + str(tr_confidence)

                    write2file(textlog, file + '\n')
                    write2file(textlog, starts[j] + '\n')
                    write2file(textlog, str(confidence[i]) + '\n')
                    write2file(textlog, transcript[i] + '\n\n')
                    results.append(message)

                    if(searchterm != ''):
                        if(searchterm in transcript[i]):
                            searchresults.append(message)

                    if(print2db):
                        print('saving to database...')
                        aplace = 'Indonesia'
                        ttime = now; atranscript = transcript[i]; vname = videoinput
                        asegment = starts[j]; aconfidence = confidence[i]
                        insert_results(connection, vname, aplace, ttime, atranscript, asegment, aconfidence)

        j=j+1

    #turn this empty until you use it again
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''

    return(results, searchresults)
#-------------------------------------------------------------------------------
