## docker file

FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt 
RUN apt-get update && apt-get install -y uvicorn
EXPOSE 3838 5432
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port",  "3838"]
