FROM python:3.9
COPY ./announcements /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "0.0.0.0:5000", "manage:app"]
