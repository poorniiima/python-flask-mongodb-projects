import os
from flask import Flask, Response, request, jsonify, make_response
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask_cors import CORS
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes
mongo_db_url = os.environ.get("MONGO_DB_CONN_STRING")

client = MongoClient(mongo_db_url)
db = client['sensors_db']
db_temp = client['temperature']

def compare_dates(date1, date2):
    if date1 == date2:
        print('ALAAARMMM!!!!!!!!')
        return 1
    else:
        return 0


def add_minutes(time_str, minutes):
    # Parse the time string into a datetime object
    time_obj = datetime.strptime(time_str, '%H.%M.%S')

    # Create a timedelta object for the specified number of minutes
    minutes_delta = timedelta(minutes=int(minutes))

    # Add the timedelta to the time object
    new_time_obj = time_obj + minutes_delta

    # Format the new time object back into the desired string format
    new_time_str = new_time_obj.strftime('%H.%M.%S')

    return new_time_str

@app.post("/api/sensors")
def add_sensor():
    now = datetime.now().replace( second= 0, microsecond= 0 )
    current_time = now.strftime("%H.%M.%S")
    _json = request.json
    print(_json)
    _json['userId'] = int(_json['userId'])
    if _json['userId'] == 4:
        _json.update({"name": "Johanna"})
    if _json['userId'] == 99:
        _json.update({"name": "Poornima"})
    if _json['userId'] == 249:
        _json.update({"name": "General"})

    if _json['alarm_Type'] == "WAKEUP":
        db.sensors.insert_one(_json)
    if _json['alarm_Type'] == "STUDY":
        modified_time = add_minutes(current_time, _json['alarm_time'])
        _json.update({"alarm_time": modified_time})
        db.sensors.insert_one(_json)
    if _json['alarm_Type'] == "STUDY_BREAK_OVER":
        modified_time = add_minutes(current_time, _json['alarm_time'])
        _json.update({"alarm_time": modified_time})
        db.sensors.insert_one(_json)

    resp = jsonify({"message": "Sensor added successfully"})
    resp.status_code = 200
    resp.headers.add('Access-Control-Allow-Origin', '*')
    print("loggerrrrr!")
    return resp

@app.post("/api/temperature")
def add_temperature():
    now = datetime.now().replace( second= 0, microsecond= 0 )
    _json = request.json
    _json.update({"timestamp": now.strftime("%m/%d/%Y %H:%M:%S")})    
    db_temp.temperature.insert_one(_json)

    resp = jsonify({"message": "Temperature added successfully"})
    resp.status_code = 200
    return resp

@app.get("/api/sensors")
def get_sensors():
    sensor_id = request.args.get('sensor_id')
    filter = {} if sensor_id is None else {"sensor_id": sensor_id}
    sensors = list(db.sensors.find(filter))

    response = Response(
        response=dumps(sensors), status=200,  mimetype="application/json")
    return response

@app.get("/api/temperature")
def get_temperature():
    temperature_id = request.args.get('temperature_id')
    filter = {} if temperature_id is None else {"temperature_id": temperature_id}
    sensors = list(db_temp.temperature.find(filter))
    length1= len(sensors)
    print("sensors[length1-1]", sensors[length1-1])

    response = Response(
        response=dumps(sensors[length1-1]), status=200,  mimetype="application/json")
    return response

@app.get("/api/activealarms")
def active_alarms():
    response="No active alarms"
    now = datetime.now().replace( second= 0, microsecond= 0 )
    current_time = now.strftime("%H.%M.%S")
    alarm_time = request.args.get('sensor_id')
    filter = {} if alarm_time is None else {"alarm_time": alarm_time}
    times = list(db.sensors.find(filter))

    for i in range(0, len(times)):
        print("current time", current_time)
        print("type current time", type(current_time))
        res = compare_dates(current_time, times[i]['alarm_time'])

        if res ==1:
            response = Response(
                response=dumps(times[i]), status=200,  mimetype="application/json")
            print (response)

    return response


@app.delete("/api/sensors/<id>")
def delete_sensor(id):
    db.sensors.delete_one({'_id': ObjectId(id)})

    resp = jsonify({"message": "Sensor deleted successfully"})
    resp.headers.add('Access-Control-Allow-Origin', '*')

    resp.status_code = 200
    return resp 

@app.put("/api/sensors/<id>")
def update_sensor(id):
    _json = request.json
    db.sensors.update_one({'_id': ObjectId(id)}, {"$set": _json})

    resp = jsonify({"message": "Sensor updated successfully"})
    resp.status_code = 200
    return resp

@app.errorhandler(400)
def handle_400_error(error):
    return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Bad request!",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 400)

@app.errorhandler(404)
def handle_404_error(error):
        return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Resource not found!",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 404)

@app.errorhandler(500)
def handle_500_error(error):
        return make_response(jsonify({"errorCode": error.code, 
                                  "errorDescription": "Internal Server Error",
                                  "errorDetailedDescription": error.description,
                                  "errorName": error.name}), 500)