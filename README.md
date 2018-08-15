# MicroBot Console

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

### 4. Run the console
    cd src
    python run.py

### 5. Go the http://127.0.0.1:16000

### 6. Quit
    ctrl + c
    deactivate


# Using gunicorn
    gunicorn -w 3 --certfile ssl/console_microbot_is.crt --keyfile ssl/console_microbot_is.key -b 127.0.0.1:5000 run:__app


# Reference

### https://github.com/afourmy/flask-gentelella
### https://github.com/klokantech/flask-firebase