# Use the Python3.7-slim image
FROM python:3.7-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file used for pip install
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy required files
COPY producer.py .

# Run the script when the app starts
CMD ["python3","producer.py"]
