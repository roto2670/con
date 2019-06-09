# MicroBot Console

## Requirment
    upper Python3.7
    redis

# 1. Develop Installation

### 1. Setup virtual environment and Execute
    pip install virtualenv
    virtualenv venv_console
    source venv_console/bin/activate

### 2. Clone the project
    git clone git@g.thenaran.com:/apps/console.git
    cd console

### 3. Install requirements
    pip install -r requirements.txt

### 4. Install docker
  * docker install referrence : https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html

### 5. redis install and run
    docker pull redis
    docker run --name some-redis redis -p 6379:6379 redis

### 6. Run the console
    cd src
    python run.py

### 7. Go the http://127.0.0.1:16000

### 8. Quit
    ctrl + c
    deactivate


# Using gunicorn
    gunicorn -w 3 --certfile ssl/mib_io.crt --keyfile ssl/mib_io.key -b 127.0.0.1:5000 run:__app


# Using MySQL for Google Cloud SQL
    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    chmod +x cloud_sql_proxy
    ./cloud_sql_proxy -instances=protacloud:us-west1:console=tcp:3306 -credential_file=console_db.json


# Live Run
    cd console/cloud_sql
    nohup ./cloud_sql_proxy -instances=protacloud:us-west1:console=tcp:3306 -credential_file=console_db.json
    cd src
    nohup gunicorn -w 3 -k gevent --certfile ssl/mib_io.crt --keyfile ssl/mib_io.key -b 127.0.0.1:5000 run:__app
    nohup celery -A worker.worker worker --loglevel=debug


# Structure![](res/cs_struct_180906.png)


# DataBase![](res/cs_db190605.png)


# Reference

#### https://github.com/afourmy/flask-gentelella
#### https://github.com/klokantech/flask-firebase
#### https://cloud.google.com/sql/docs/mysql/connect-external-app#python
#### https://github.com/GoogleCloudPlatform/getting-started-python/blob/504b3d550b551502cfe96f32542c31b232135eff/2-structured-data/config.py
#### https://flask-monitoringdashboard.readthedocs.io/en/master/index.html


# WordCloud

#### https://github.com/d3/d3
#### https://github.com/jasondavies/d3-cloud
#### https://github.com/wvengen/d3-wordcloud


# Console Document

#### Storyboard [Link](https://ovenapp.io/view/p6S16zsgDcDSXPj6ZdUVxql7ElvMV2Bn/bhthA)

#### Message [Link](https://docs.google.com/spreadsheets/d/1mGpmTbqgb7dihBFkI8bSTq0tT2QMWC1soVBa4q-7Bbg/edit#gid=1738330008)

#### Message Slide [Link](https://docs.google.com/presentation/d/175Wa5WUp-VasoTu4giINSe1Enr81K-WYP81R6c4OWc4/edit#slide=id.p)
