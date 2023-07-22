# Use the latest bitnami spark image
FROM bitnami/spark:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file used for pip install
COPY requirements.txt ./

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy required files
COPY cassandra_handler.py ./
COPY process.py ./

# Run the script when the app starts
CMD ["python3", "process.py"]

