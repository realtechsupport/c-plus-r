#!/usr/bin/env python3
#av_helper.py (python3)
#utilities for stt via google apt
#jan 2019 - jan 2020
#author: realtechsupport

#-------------------------------------------------------------------------------
import os, sys, io
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
