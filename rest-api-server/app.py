import os
from flask import Flask, Response, request, jsonify, make_response
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime

load_dotenv()

app = Flask(__name__)
mongo_db_url = os.environ.get("MONGO_DB_CONN_STRING")

client = MongoClient(mongo_db_url)
db = client['sensors_db']


def compare_dates(date1, date2):
    # convert string to date
    dt_obj2 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S")

    if date1 == dt_obj2:
        print('ALAAARMMM!!!!!!!!')
        return 1
    else:
        return 0


@app.get("/api/sensors")
def get_sensors():
    sensor_id = request.args.get('sensor_id')
    filter = {} if sensor_id is None else {"sensor_id": sensor_id}
    sensors = list(db.sensors.find(filter))

    response = Response(
        response=dumps(sensors), status=200,  mimetype="application/json")
    return response

@app.get("/api/activealarms")
def active_alarms():
    response="No active alarms"
    now = datetime.now().replace( second= 0, microsecond= 0 )
    alarm_time = request.args.get('sensor_id')
    filter = {} if alarm_time is None else {"alarm_time": alarm_time}
    times = list(db.sensors.find(filter))

    for i in range(0, len(times)):
        print("i",i)
        print("times[i]", times[i])
        res = compare_dates(now, times[i]['alarm_time'])

        if res ==1:
            response = Response(
                response=dumps(times[i]), status=200,  mimetype="application/json")
            print (response)

    return response


@app.delete("/api/sensors/<id>")
def delete_sensor(id):
    db.sensors.delete_one({'_id': ObjectId(id)})

    resp = jsonify({"message": "Sensor deleted successfully"})
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