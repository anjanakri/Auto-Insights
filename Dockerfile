# 1. Use an official Python runtime
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the app code
COPY . .

# 5. Command to run the app
CMD ["python", "autoinsights_adk_python.py"]