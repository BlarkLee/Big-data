# MIT Big-Data program
This is a project followed with Dr. Fan Zhang from MIT LIGO laboratory to integrate the applicaton of CNN with Docker and Cassandra.
## Introduction 
 To generalize this project, a trained-model of Convolutional Neural Network(CNN) is deployed into the container using Docker; Two types of interface is designed using Flask for users to submit their images; The program then processes the image with the trained-model to predict a reliable result and expose the result back to the front page with RESTful API tech. At the same time, the result(the prediction and the testing time) would be deployed and stored in the database Apache Cassandra.
 ## Train the model
 The first step is to train a CNN model. In this project, I chose a classic example the Mnist, namely the model which is able to detect the image of number from 0 to 9. I download the training set from the official site of Tensorflow and use the CNN model the official site offers, we set the training times as 20000, and saved the trained CNN model 

