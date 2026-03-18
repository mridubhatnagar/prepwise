# Efficient stack ordering for building and running Python applications
# - Keep the image size small
# - Use a Python base image
# - Use a .dockerignore file to exclude unwanted files
# - Install the package dependencies first
# - Copy the application code to the container at the last

# Use the official Python base image with Python 3.8
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /prepWise

# Copy the application code to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port that the FastAPI app will run on
EXPOSE 8000

# Copy the application code to the container at the last
COPY . .

# Run the Fast API application, use fastapi default port 8000.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]