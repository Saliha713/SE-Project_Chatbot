#!/bin/bash

# -----------------------------
# Backend Setup
# -----------------------------
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r Backend/requirements.txt

# -----------------------------
# Frontend Setup
# -----------------------------
echo "Installing Node.js dependencies and building React app..."
cd Frontend
npm install
npm run build
cd ..

# -----------------------------
# Start Backend
# -----------------------------
echo "Starting FastAPI server..."
python -m uvicorn Backend.main:app --host 0.0.0.0 --port $PORT
