from flask import Flask, render_template, jsonify, request
from work_data import Data_Cleaned

app = Flask(__name__)
classroom = Data_Cleaned()
@app.route("/")
def index():
    return jsonify({"message": "Classroom"})

@app.route("/classroom")
def get_class():
    return jsonify({"classroom" : classroom.query_classroom, "message" : "Classroom's list"})

@app.route("/available/<day>/<int:hour>")
def availables_classroom(day, hour):
    return({"classroom": classroom.classroom_availables(day,hour, request.args.get("room"), request.args.get("next_class"))})

if (__name__=="__main__"):
    app.run(debug=True, port=5000)