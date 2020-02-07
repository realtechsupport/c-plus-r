#!/usr/bin/env python3
# utlities.py (python3)
# additional helper functions
# Catch+Release
# Flask interface for linux computers
# experiments in knowledge documentation; with an application to AI for ethnobotany
# jan 2020
# tested on ubuntu 18 LTS, kernel 5.3.0
#-------------------------------------------------------------------------------
import sys, os, io, time, datetime, glob
import argparse
from os import listdir
from os.path import isfile, join
from os import environ, path
import json as simplejson
import subprocess
import psutil, shutil
from shutil import copyfile
import signal, wave
import contextlib
import numpy as np
from random import *
import sqlite3
#import nltk
#------------------------------------------------------------------------------
def removefiles(app, patterns, locations, exception):
    for loc in locations:
        os.chdir(app.config[loc])
        for pat in patterns:
            for file in glob.glob(pat):
                if(exception in file):
                    pass
                else:
                    os.remove(file)
#------------------------------------------------------------------------------
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
#-------------------------------------------------------------------------------
def write2file(filename, comment):
    file = open(filename, "a")
    value = file.write(comment)
    file.close()
#-------------------------------------------------------------------------------
def get_context():
    print('add contextual information for the video annotation')
    context = {}
    context['videomaker']  = input("who shot the video? ")
    context['annotator'] = input("who is making the annotations? ")
    context['location'] = input("where was the video made? ")
    context['content'] = input("what content does the video show? ")
    context['projecthistory'] = input("mention the project history, if applicable ")
    context['comments'] = input("other comments ? ")
    return(context)
#-------------------------------------------------------------------------------
def get_location(namedlocation):
    if (namedlocation == 'ip'):
        loc = geocoder.ip('me')
    else:
        loc = geocoder.google(namedlocation)
        print(loc)
    return(loc.latlng)
#-------------------------------------------------------------------------------
def rename_all(directory, imgname, offset=0):
    files = filter(os.path.isfile, glob.glob(directory + "*"))
    files = list(files)             #for python3
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    print(files)

    for i in range (offset, len(files)):
        print (i, files[i])
        newname = directory + imgname + str(i) + '.jpg'
        os.rename(files[i], newname)
#-------------------------------------------------------------------------------
def create_connection(datapath, db_file):
    """
    create a database connection to the database
    :param db_file: database file
    :return: Connection object or None
    """
    os.chdir(datapath)
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return (conn)
#-------------------------------------------------------------------------------
def create_table(connection):
    cursor = connection.cursor()
    sql_command = """
    CREATE TABLE IF NOT EXISTS events (
    test_number INTEGER PRIMARY KEY,
    aname VARCHAR(30),
    place VARCHAR(20),
    atime DATE,
    transcript TEXT,
    segment TEXT,
    confidence REAL);"""
    cursor.execute(sql_command)
#-------------------------------------------------------------------------------
def select_print_all_tasks(conn):
    """
    Query all rows in the events table
    :param conn: the Connection object
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = conn.cursor()
    cur.execute("SELECT * FROM events")
    rows = cur.fetchall()

    for row in rows:
        print(row)
#-------------------------------------------------------------------------------
def select_transcripts(connection):
    """
    :input: the Connection object
    :return: transcripts
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = connection.cursor()
    cur.execute("SELECT transcript FROM events")
    rows = cur.fetchall()
    return(rows)
#-------------------------------------------------------------------------------
def select_confidencelevels(connection):
    """
    :input: the Connection object
    :return: transcripts
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = connection.cursor()
    cur.execute("SELECT confidence FROM events")
    rows = cur.fetchall()
    return(rows)
#-------------------------------------------------------------------------------
def select_segments(connection):
    """
    :input: the Connection object
    :return: transcripts with min confidence levels
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = connection.cursor()
    cur.execute("SELECT segment FROM events")
    segment_rows = cur.fetchall()
    return(segment_rows)
#-------------------------------------------------------------------------------
def select_transcripts_confidencelevel(connection, confidencelevel):
    """
    :input: the Connection object
    :return: transcripts with min confidence levels
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = connection.cursor()
    cur.execute('''SELECT transcript FROM events WHERE confidence >?''', (confidencelevel,))
    rows = cur.fetchall()
    return(rows)
#-------------------------------------------------------------------------------
def select_transcripts_segments_confidencelevel(connection, confidencelevel):
    """
    :input: the Connection object
    :return: transcripts with min confidence levels
    """
    connection.row_factory = lambda cur, row: row[0]
    cur = connection.cursor()
    cur.execute('''SELECT transcript FROM events WHERE confidence >?''', (confidencelevel,))
    transcript_rows = cur.fetchall()
    cur.execute('''SELECT segment FROM events WHERE confidence >?''', (confidencelevel,))
    segment_rows = cur.fetchall()

    results = []
    for i in  range (0,len(transcript_rows)):
        temp = segment_rows[i], transcript_rows[i]
        results.append(temp)

    return(results)
#-------------------------------------------------------------------------------
def insert_results_closedb(connection, vname, aplace, ttime, atranscript, asegment, aconfidence):
    cursor = connection.cursor()
    command = """INSERT INTO events (test_number, aname, place, atime, transcript, segment, confidence)
    VALUES (NULL, "{aname}", "{place}", "{atime}", "{transcript}", "{segment}", "{confidence}");"""

    sql_command = command.format(aname=vname, place=aplace, atime=ttime, transcript=atranscript, segment=asegment, confidence=aconfidence)
    cursor.execute(sql_command)
    connection.commit()
    connection.close()
#-------------------------------------------------------------------------------
def insert_results(connection, vname, aplace, ttime, atranscript, asegment, aconfidence):
    cursor = connection.cursor()
    command = """INSERT INTO events (test_number, aname, place, atime, transcript, segment, confidence)
    VALUES (NULL, "{aname}", "{place}", "{atime}", "{transcript}", "{segment}", "{confidence}");"""

    sql_command = command.format(aname=vname, place=aplace, atime=ttime, transcript=atranscript, segment=asegment, confidence=aconfidence)
    cursor.execute(sql_command)
    connection.commit()
    #connection.close()
#-------------------------------------------------------------------------------
