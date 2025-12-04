#!/bin/bash

# Navigate to backend
cd Backend

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
