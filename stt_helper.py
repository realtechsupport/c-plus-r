#!/usr/bin/env python3
# stt_helper.py
# utilities for stt via google apt
# Catch+Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
# jan 2020
# tested on ubuntu 18 LTS, kernel 5.3.0
#-------------------------------------------------------------------------------
import os, sys, io
from utilities import *
from av_helper import *
#-------------------------------------------------------------------------------
def transcribe_longrunning_audio(speech_file, language, maxattempts):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,language_code = language)

    for i in range (0,maxattempts):
        try:
            operation = client.long_running_recognize(config, audio)
            print('\nWaiting for S2T operation to complete on: ', speech_file)
            response = operation.result(timeout=90)
            break
        except:
            print('error connecting to API service...retrying... chunks too long?')
            pass

    transcript = []
    confidence = []
    try:
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            transcript.append(result.alternatives[0].transcript)
            confidence.append(result.alternatives[0].confidence)
    except:
            pass

    return(transcript, confidence)

#-------------------------------------------------------------------------------
def transcribe_file_with_word_time_offsets(app, audiofile_1ch, videonamepath, key, language, maxattempts, nimages, tconfidence):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # local variables to transcribe_file_with_word_time_offsets
    start_t = " -ss 00:00:"                                 #start of video stream
    dur = " -t 1.0"                                         # 1 second duration after detection of utterance ...
    start_set = " -r " + str(nimages)                       # set in UI
    end_set = " -f image2 "
    nums =  "%d.jpg"
    av_call = "avconv -loglevel panic -i "
    v_resolution = get_video_resolution(videonamepath)      #set in UI
    scale = " -s " + v_resolution
    keyphrases = [{"phrases":key}]

    with io.open(audiofile_1ch, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code = language,
        enable_word_time_offsets=True,
        use_enhanced = True,                #not sure here
        #enable_word_confidence=True,       #not available in this version?
        max_alternatives = 5,
        model= 'command_and_search',
        speech_contexts = keyphrases)

    '''
    for i in range (0,maxattempts):
        try:
            print('\nWaiting for S2T operation to complete on: ', speech_file)
            response = client.recognize(config, audio)
            print('response is: ', response)
            break
        except:
            print('error connecting to API service...retrying... chunks too long?')
            time.sleep(1)
            pass
    '''
    response = client.recognize(config, audio)

    try:
        for result in response.results:
            alternative = result.alternatives[0]
            confidence = alternative.confidence
            stream = (u'Transcript: {}'.format(alternative.transcript))
            details = ('First alternative of result {}'.format(result))
            #print(stream); print(details)
            #collecting images
            if(confidence >= tconfidence):
                for word_info in alternative.words:
                    word = word_info.word
                    word = word.lower()

                    if word in key:
                        selectit = 1
                        #print('found word in keys')
                    else:
                        selectit = 0

                    start_time = word_info.start_time
                    end_time = word_info.end_time
                    begin = round(start_time.seconds + start_time.nanos * 1e-9)

                    if(begin < 10):
                        start = start_t + "0" + str(begin)
                    else:
                        start = start_t + str(begin)

                    #print(word + ', ' + str(start_time.seconds + start_time.nanos * 1e-9) + ', ' + str(end_time.seconds + end_time.nanos * 1e-9) + '\n')
                    if(selectit):
                        print(' > saving images labeled as: ', word)
                        dir_t = os.path.join(app.config['IMAGES'], word)
                        if not os.path.exists(dir_t):
                            os.makedirs(dir_t)

                        out = dir_t + '/' + word + "_" + str(begin) + "_" + nums
                        command = av_call + videonamepath + start_set + ' ' + start + dur + scale + end_set + out
                        subprocess.call(command, shell=True)

            else:
                print('result below confidence threshold... disregarding')

        rename_all(dir_t, offset=0)

    except:
        pass
