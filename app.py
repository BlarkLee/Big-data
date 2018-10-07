import sys
import tensorflow as tf
from PIL import Image
import time
import logging
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


def predictint(imvalue):
    
    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    
    def weight_variable(shape):
      initial = tf.truncated_normal(shape, stddev=0.1)
      return tf.Variable(initial)
    
    def bias_variable(shape):
      initial = tf.constant(0.1, shape=shape)
      return tf.Variable(initial)
       
    def conv2d(x, W):
      return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
    
    def max_pool_2x2(x):
      return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')   
    
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    
    x_image = tf.reshape(x, [-1,28,28,1])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)
    
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])
    
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)
    
    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])
    
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    
    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])
    
    y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    
    init_op = tf.global_variables_initializer()
    saver = tf.train.Saver()

    with tf.Session() as sess:
        sess.run(init_op)
        saver.restore(sess, "model2.ckpt")
        #print ("Model restored.")
        prediction=tf.argmax(y_conv,1)
        return prediction.eval(feed_dict={x: [imvalue],keep_prob: 1.0}, session=sess)


def imageprepare(directory):
    im = Image.open(directory).convert('L')
    temp = list(im.getdata()) #get pixel values
    new = [ (255-x)*1.0/255.0 for x in temp] 
    return new
    



def createKeySpace(prediction,testingtime):
    cluster = Cluster(contact_points=['0.0.0.0'],port=9042)
    session = cluster.connect()
    log.info("Creating keyspace...")
    try:
        session.execute("""USE bleekeyspace""")
        
        params=[prediction, testingtime]
        session.execute("""
                        INSERT INTO CNN_table (prediction,time)
                        VALUES ( %s,%s)""",params)
        
        
        log.info("selecting...")
        session.execute(""" SELECT * FROM CNN_table """)[0]
    
    except:
        KEYSPACE = "bleekeyspace"
        session.execute("""
                        CREATE KEYSPACE %s
                        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                        """ % KEYSPACE)     
        
        log.info("setting keyspace...")
        session.set_keyspace(KEYSPACE)

        log.info("creating table...")
        session.execute("""
                        CREATE TABLE CNN_table (
                                prediction text,
                                time text,
                                PRIMARY KEY (prediction,time)
                                )
                        """)
            
        log.info("inserting data...")
        params=[prediction, testingtime]
        session.execute("""
                        INSERT INTO CNN_table (prediction,time)
                        VALUES ( %s,%s)""",params)
        
        
        log.info("selecting...")
        session.execute(""" SELECT * FROM CNN_table """)[0]
        
        
        
app = Flask(__name__)
@app.route('/', methods=['GET'])
def hello_form():
    return '''<form action="/" method="post">
              <h> Hello! Welcome to Blark's Mnist-Predicting page</h>
              <p> Please enter your name:</p>
              <p><input name="entername"></p>
              <p><button type="submit">login</button></p>
              </form>'''
@app.route('/', methods=['POST'])
def hello():
    if request.form["entername"]=='blee' or request.form["entername"]=='fzhang':
            return '''<h>Predict your image with the route '/upload' or '/predict', Blark recommands you to use the former cuz it's well-maintained. Go ahead, never look back!!!</h>'''
    
    return '''<h>Blark doesn't know you!!!</h>'''



UPLOAD_FOLDER = '/home/blark/MIT_bigdata/Dockerfile'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bmp'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)
            return redirect(url_for('uploaded_file',filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload your testing image please</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Predict>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        imvalue = imageprepare(filename)
        starttime=time.time()
        try:
            predint = predictint(imvalue)[0]
            endtime=time.time()
            testing_time=endtime-starttime
            try:
                createKeySpace(str(predint),str(testing_time))
                return '''<h3>Blark is magically predicting......</h3>
                    <b>The predicion of this image is "%s" ,the running time to process the image is "%s" second.</b>'''%(predint,testing_time)
            except:
                return '''<h3>Can't put the result into Cassandra......</h3>'''
        except:
            return '''<h3>Can't predict this image......'''
                  
    except:
        return '''<b>Blark has tried, but he can't work it out......</b>'''    





@app.route('/predict', methods=['GET'])
def predict_form():
    return '''<form action="/predict" method="post" enctype="multipart/form-data">
              <h>Upload your testing image please</h>
              <input type="file" name="photo"/>
              <input type="submit" value="Predict" class="button-new" style="margin-top:15px;"/>
              </form>'''
@app.route('/predict', methods=['POST'])
def predict():
    try:
        img=request.files["photo"]
        img.save(secure_filename(img.filename))
        imvalue = imageprepare(img.filename)
        starttime=time.time()
        try:
            predint = predictint(imvalue)[0]
            endtime=time.time()
            testing_time=endtime-starttime
            try:
                createKeySpace(str(predint),str(testing_time))
                return '''<h3>Blark is magically predicting......</h3>
                        <b>The predicion of this image is "%s" ,the running time to process the image is "%s" second.</b>'''%(predint,testing_time)
            except:
                return '''<h3>Can't put the result into Cassandra......</h3>'''
        except:
            '''Can't predict this image......'''
                  
    except:
        return '''<b>Blark has tried, but he can't work it out......</b>'''




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)