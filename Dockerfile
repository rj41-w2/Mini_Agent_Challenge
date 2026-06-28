# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python FastAPI backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend files
COPY backend/ ./

# Copy built frontend files
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Expose Hugging Face Spaces default port
EXPOSE 7860

# Run FastAPI server
CMD ["python", "sorter.py"]
