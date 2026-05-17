FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY module_b_checking.py .
EXPOSE 5002
CMD ["uvicorn", "module_b_checking:app", "--host", "0.0.0.0", "--port", "5002"]