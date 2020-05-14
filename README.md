# c-plus-r
catch and release tests

Introduction

Catch & Release (C+R) is a collection of procedures that allow you to apply machine learning classification to field videos. C+R’s goal is to facilitate the creation of under-represented knowledge in machine learning in general, and experimental datasets for neural network image classification in particular. C+R allows anyone with a mobile phone to create viable datasets for image classification and to train state of the art convolutional neural networks with them.

Furthermore, C+R can extract text from video. It can extract labels from video and use them as labels for
image categories associated with the utterance.

This software and the bali-26 dataset are the basis for the ‘Return to Bali’ project that explores machine learning to support the representation of ethnobotanical knowledge and practices in Central Bali.
http://www.realtechsupport.org/new_works/return2bali.html 

C+R can help you create machine learning datasets or serve as a companion while studying convolutional neural network systems. If you want to use it for a specific research need, for instructional purposes or if you would like to contribute to making a global alternate image collection for machine learning training, contact the repository owner (marcbohlen@protnmail.com).


License

Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
Cite this software project as follows: ‘Catch&Release version1’


Platform Information

C+R runs on Linux under Python3  and Flask with Chrome or Firefox. C+R uses the PyTorch framework to train and test the image classifiers. Library versions and dependencies are given in the requirements.txt file. C+R has been tested on Ubuntu 18.04 TLS with kernel 5.3.0 on images sourced from .mp4 and .webm video formats (HD [1920 x 1080] at 30f/s; .mp4  H.264 encoded) from multiple (android OS) mobile phones and GoPro Hero 6 action cameras.
