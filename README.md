# MIT Big-Data program
This is a project followed with Dr. Fan Zhang from MIT LIGO laboratory to integrate the applicaton of CNN with Docker and Cassandra.
## A brief introduction to this program
 To generalize this project, a trained-model of Convolutional Neural Network(CNN) is deployed into the container using Docker; Two types of interface is designed using Flask for users to submit their images; The program then processes the image with the trained-model to predict a reliable result and expose the result back to the front page with RESTful API tech. At the same time, the result(the prediction and the testing time) would be deployed and stored in the database Apache Cassandra.

