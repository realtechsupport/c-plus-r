# c-plus-r


<b> <i> Updates December 2020 </b> </i>

-Do not use the zip download option - It seems to not include all files.
Instead download with git clone from the command line: git clone https://github.com/realtechsupport/c-plus-r.git

-If you intend to use this program with Chrome on Ubuntu 20.04 LTS, disable Chrome's hardware accelleration (settings/advanced/system)
	
	
	
<b>Introduction</b>

Catch & Release (C&R) is a collection of procedures that allow one to apply machine learning classification onto field videos. C&R’s goal is to facilitate the creation of under-represented knowledge in machine learning in general, and experimental datasets for neural network image classification in particular. C&R allows anyone with a mobile phone and a laptop to create viable datasets for image classification (and to train state of the art convolutional neural networks with these datasets).

Furthermore, C&R can extract text from video. It can extract labels from video and use them as labels to generate
image categories associated with the utterance.

This software and the bali-26 dataset are the basis for the ‘Return to Bali’ project that explores machine learning to support the representation of ethnobotanical knowledge and practices in Central Bali. http://www.realtechsupport.org/new_works/return2bali.html 

<b>License</b>

Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
Cite this project as: Catch&Release version1


<b>Context</b>

C&R runs on Linux and macOS under Python3 and Flask with Chromium or Firefox.

C&R uses the PyTorch framework to train and test image classifiers and connects to the Google Speech API (free) for speech processing. Library versions and dependencies are given in the requirements file.
C&R has been tested on a desktop (i7-4770 CPU with 16GB of memory) and a laptop (i7-3667 CPU with 8GB of memory) under Ubuntu (18.04 TLS under kernels 5.2.8 and 5.3.0 ) and under macOS (Catalina) with images sourced from .mp4 and .webm video (HD [1920 x 1080] at 30f/s; .mp4 H.264 encoded) from multiple (android
OS) mobile phones and GoPro Hero 6 action cameras.

Recommended browser: Chromium on Ubuntu, Chrome on MAC.

Install Chromium on Ubuntu:

	sudo apt install -y chromium-browser

Install the free Classic Cache Killer:

	https://chrome.google.com/webstore/detail/classic-cache-killer/kkmknnnjliniefekpicbaaobdnjjikfp?hl=en


<b>Installation</b>

Clone the C&R repository on GitHub
Open a terminal window and type:

	git clone https://github.com/realtechsupport/c-plus-r.git

Cd to the c-plus-r directory and  run the following commands to update your python environment:

	chmod +x basics.sh
	sudo sh basics.sh
	(this script updates your ubuntu installation and requires sudo to do so.)

Create a virtual environment:

	python3 -m venv env

Activate the environment:

	source ./env/bin/activate

Cd to to the c-plus-r directory again.
Install Requirements and Dependencies.
This process may take 30 minutes or so.

	pip3 install -r requirements.txt


Generate an STT key (optional)

While there are multiple providers of Speech to Text services, the most effective offering with the widest range of languages is at this moment provided by Google. If you want to make use of the text from video extraction you should obtain an access key to the Google Speech API. Creation of this key is free of charge and you can use it in this software at no cost as C+R operates within free limits of the API. However, you do require a google account in order to create the key. If that is not palatable, skip the sections that make use of the Speech API.

Instructions to generate a key (https://cloud.google.com/text-to-speech/docs/quickstart-protocol):

    1. In the Cloud Console, go to the Create service account key page.
    2. From the Service account list, select New service account.
    3. In the Service account name field, enter a name.
    4. Don't select a value from the Role list. No role is required to access this service.
    5. Click Create.
    6. Click Create without role. A JSON file that contains your key downloads to your computer.
    7. Save the JSON file to the C+R project.


<b>Launch</b>

Activate the virtual environment:

	source ./env/bin/activate

<b>Start</b>

Start C+R (in the c-plus-r directory):

	on ubuntu: 	python3 main.py ubuntu chromium no-debug
	on mac: 	python3 main.py mac chrome no-debug

Specify all three items: OS, browser and debug mode. Supported OS: Ubuntu and Mac OS. Supported browsers on Ubuntu:
Chromium and Firefox (less stable). To run in debug mode replace ’no-debug’ with ‘debug’.


<b>Stop</b>

Stop the app from the terminal: ctrl-c
<br>
Exit environment at the terminal: ctrl-d

<i>Check the README.pdf file in the repository for a detailed description on how to use the modules in C&R.</i>
