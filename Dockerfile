# REQUIRED structure — your Dockerfile must include all of these


# 1. Use an official slim Python base image (python:3.11-slim or newer)
FROM python:3.11-slim


# 2. Set a working directory inside the container
WORKDIR /app


# 3. Copy requirements BEFORE the rest of the code (layer caching)
COPY requirements.txt .


# 4. Install Python dependencies (no cache to keep image small)
RUN pip install --no-cache-dir -r requirements.txt


# 5. Copy the rest of the application source code
COPY . .


# 6. Expose the Flask port
EXPOSE 5000


# 7. Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production


# 8. Start the app (use CMD, not ENTRYPOINT, so it can be overridden)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

