#!/bin/bash
# RTS, feb 2020
#-------------------------------------------
clear
echo "WELCOME - basics for C+R installaton "

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3-dev -y
sudo apt-get install build-essential python3-dev -y
sudo apt-get install python3-venv -y
sudo apt-get install ffmpeg -y
sudo apt-get install sox -y

<<<<<<< HEAD
echo "installed python3, python3dev, python3-venv, ffmpeg "
=======
echo "installed python3, python3dev, python3-venv, ffmpeg, sox "
>>>>>>> a52f369e2850664d0576379b67aa3e9f488487f0

echo "hit ctrl d to close this session"
exit 0

