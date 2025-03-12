FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV DISCORD_TOKEN="YOUR_DISCORD_TOKEN"
ENV TAUTULLI_TOKEN="YOUR_TAUTULLI_TOKEN"

CMD ["python", "main.py"]