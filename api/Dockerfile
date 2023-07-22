# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Copy the requirements file used for pip install
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run the script when the app starts
CMD ["python3", "app.py"]
