# Use an official Python runtime as a parent image
FROM python:3.6

# Set the working directory to /app
WORKDIR /app/

# Copy the current directory contents into the container at /app
COPY . /app/
ADD checkpoint /app/
ADD model2.ckpt.data-00000-of-00001 /app/
ADD model2.ckpt.index /app/
ADD model2.ckpt.meta /app/
#COPY ~/MIT_bigdata/Dockerfile  ~/MIT_bigdata/Dockerfile

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "app.py"]
