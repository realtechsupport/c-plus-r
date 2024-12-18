#!/bin/bash
# RTS, feb 2020
# updated nov 2024 (libcurl4)
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
sudo apt-get install libcurl4-openssl-dev

echo "installed python3, python3dev, python3-venv, ffmpeg "
echo "installed python3, python3dev, python3-venv, ffmpeg, sox "

echo "hit ctrl d to close this session"
exit 0

