from flask import Flask, render_template, jsonify, request
from sqlalchemy import func
from work_data import Data_Cleaned
import datetime as dt

#Wrapped function
from functools import wraps

#ENVIROMENT VARIABLES
from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

token_api = environ["API_KEY_INTEC"]
app = Flask(__name__)
classroom = Data_Cleaned()

# Authentification
def authentification_toke(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        key = request.args.get("key")
        if (key==None or key!=token_api):
            return jsonify({"message": "Without access"})
        return function(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return jsonify({"message": "Classroom"})

@app.route("/classroom")
@authentification_toke
def get_class():
    room = request.args.get("classroom")
    if room!=None:
        return jsonify({"classroom" : classroom.query_classroom[room], "message" : "Classroom's list"})
    return jsonify({"classroom" : classroom.query_classroom, "message" : "Classroom's list"})

@app.route("/classroom/<class_>")
@authentification_toke
def get_shedule_by_class(class_):
    if (class_ in classroom.query_classroom.keys()):
        return jsonify({"classroom" : classroom.query_classroom[class_], "message" : "Classroom's list"})
    else:
        return jsonify({"error": 404, "message": "That classrooom wasn't found"})

@app.route("/available")
@authentification_toke
def get_availables():
    day = request.args.get('day')
    hour = request.args.get('hour')
    area = request.args.get("area")
    comprobate = request.args.get("comprobate")

    # Validation of the information
    if (day==None or day.capitalize() not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]):
        day = dt.datetime.now().strftime("%A")
    if (hour==None):
        hour = int(dt.datetime.now().strftime("%H"))
    if (area!=None):
        area = area.upper()
    if (comprobate!=None):
        comprobate = True

    day = day.capitalize()
    hour = int(hour)

    return({"classroom": classroom.classroom_availables(day,hour, area, comprobate)})

if (__name__=="__main__"):
    app.run(debug=True, port=5000)