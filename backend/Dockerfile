# Step 1: Use official Python image
FROM python:3.11-slim

# Step 2: Set work directory inside container
WORKDIR /app

# Step 3: Install system dependencies (optional: Pillow & image processing libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy requirements.txt and install Python deps
COPY requirements.txt .

# Increase pip timeout and split torch installation for reliability
RUN pip install --no-cache-dir torch torchvision --default-timeout=200 \
    && pip install --no-cache-dir -r requirements.txt --default-timeout=200

# Step 5: Copy backend code
COPY . .

# Step 6: Expose port
EXPOSE 8000

# Step 7: Command to run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


