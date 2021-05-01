# base image  
FROM python:3.8   
# setup environment variable  
ENV DockerHOME=/home/app/gbahotel
RUN mkdir -p $DockerHOME  
WORKDIR $DockerHOME
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1   
RUN pip install --upgrade pip  
COPY . $DockerHOME  
RUN pip install -r requirements.txt   
EXPOSE 8000   
CMD python manage.py runserver 0.0.0.0:8000