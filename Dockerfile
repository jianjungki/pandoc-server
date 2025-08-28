# Use an official Python runtime as a parent image
FROM python:3.12.11-slim
# Install pandoc
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    latexmk \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Verify pandoc installation
RUN pandoc --version

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application
COPY ./main.py /app/main.py

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]