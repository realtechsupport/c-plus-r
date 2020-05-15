# c-plus-r

<b>Introduction</b>

Catch & Release (C+R) is a collection of procedures that allow you to apply machine learning classification to field videos. C+R’s goal is to facilitate the creation of under-represented knowledge in machine learning in general, and experimental datasets for neural network image classification in particular. C+R allows anyone with a mobile phone to create viable datasets for image classification and to train state of the art convolutional neural networks with them.

Furthermore, C+R can extract text from video. It can extract labels from video and use them as labels for
image categories associated with the utterance.

This software and the bali-26 dataset are the basis for the ‘Return to Bali’ project that explores machine learning to support the representation of ethnobotanical knowledge and practices in Central Bali.
http://www.realtechsupport.org/new_works/return2bali.html 

C+R can help you create machine learning datasets or serve as a companion while studying convolutional neural network systems. If you want to use it for a specific research need, for instructional purposes or if you would like to contribute to a viable alternative to ImageNet for machine learning training, contact the repository owner (marcbohlen@protnmail.com).


<b>License</b>

Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
Cite this project as: Catch&Release version1


<b>Context</b>

C+R runs on Linux under Python3  and Flask with Chromium or Firefox. C+R uses the PyTorch framework to train and test the image classifiers and to access the Google Speech API (free) for speech processing. Library versions and dependencies are given in the requirements file. 
C+R has been tested on a desktop (i7-4770 CPU / 16GB of memory) and a laptop (i7-3667 CPU  / 8GB of memory) with Ubuntu 18.04 TLS under kernels 5.2.8 and 5.3.0 with images sourced from .mp4 and .webm video (HD [1920 x 1080] at 30f/s; .mp4  H.264 encoded) from multiple (android OS) mobile phones and GoPro Hero 6 action cameras.


<b>Installation</b>

Clone the C+R repository on GitHub
Open a terminal window and type:

	git clone https://github.com/realtechsupport/c-plus-r.git
	Username for 'https://github.com': realtechsupport
	Password for 'https://realtechsupport@github.com'
	<enter the access token> 

Cd to the c-plus-r directory and  run the following commands to update your python environment:

	chmod +x basics.sh
	sh basics.sh

Create a virtual environment:

	python3 -m venv env

Activate the environment:

	source ./env/bin/activate

Install Requirements and Dependencies

	pip3 install -r requirements.txt


Generate an STT key (optional)

While there are multiple providers of Speech to Text services, the most effective offering with the widest range of languages is at this moment Google. If you want to make use of the text from video extraction you should get an access key to the Google Speech API. Creation of the key is free and you can use it in this software at no cost as C+R operates within free limits of the API. However, you do need a google account to create the key. If that is not palatable, skip the sections that use the Speech API

Instructions to generate a key:

    1. Navigate to the APIs & Services->Credentials panel in Cloud Platform Console.
    2. Select Create credentials, then select API key from the dropdown menu.
    3. Click the Create button. ... 
    4. Once you have the API key, download it and create a JSON file.
    5. Save to the C+R project

<b>Launch</b>

Activate the virtual environment:

	source ./env/bin/activate

<b>Start</b>   


	python3 main.py browser debug_mode

browser = firefox or chromium; debug_mode = debug or no-debug. 
The terminal window will display comments. You should see the launch screen in a browser window.  


<b>Stop</b>

Stop the app from the terminal: ctrl-c
<br>
Exit environment at the terminal: ctrl-d

<i>Check the README.pdf file in the repository for information on how to use C+R.</i>
