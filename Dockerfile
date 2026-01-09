# Use Python 3.12 slim image (smaller, faster)
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (this layer gets cached if requirements.txt unchanged)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
