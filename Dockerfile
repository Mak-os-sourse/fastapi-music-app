FROM python
WORKDIR /app
ADD / /app
RUN apt update && apt upgrade
RUN pip install -r requierments.txt
ENV PYTHONPATH=/app
CMD ["python", "src/app/app.py"]