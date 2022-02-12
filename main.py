from turtle import heading
from flask import Flask, flash, redirect, request, render_template
import pymongo
from pymongo import MongoClient
import json 
from bson import json_util


cluster = MongoClient("mongodb+srv://Sasith:sk11@cluster0.qrglo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster["renewable_energy"]
collection = db["electricity"]

#collection.insert_one({"_id":"EMERASF1", "regionid":"QLD1", "scadavalue":"15"})

app = Flask(__name__)

@app.route("/checkBattery", methods=["GET"])
def check_battery():
    allBatteries = list(collection.find({}))
    return json.dumps(allBatteries, default=json_util.default)

@app.route("/chargeBattery")
def charge():
    allBatteries = list(collection.find({}))
    return render_template("charge.html", data=allBatteries) #pass json respone to html

@app.route("/chargeBattery", methods=["POST"])
def charge_battery():

    _id = request.form['_id']
    regionid = request.form['regionid']
    scadavalue = float(request.form['scadavalue'])
    
    existing_battery = collection.find({"_id":_id})

    #issue - even existing_battery is empty,it gone throgh the if condition
    if existing_battery:
        for ex_battery in existing_battery:
            old_scadavalue = float(ex_battery["scadavalue"])
            updated_scadavalue = scadavalue+old_scadavalue
        collection.find_one_and_update({"_id": _id}, {"$set": {"regionid": regionid, "scadavalue": updated_scadavalue}}, upsert=True)
        #collection.insert_one({"_id": _id, "regionid": regionid, "scadavalue": scadavalue})
   
    return redirect("/chargeBattery")


@app.route("/dischargeBattery")
def discharge():
    allBatteries = list(collection.find({}))
    return render_template("discharge.html", data=allBatteries)

@app.route("/dischargeBattery", methods=["POST"])
def sell_electricity():
 
    _id = request.form['_id']
    regionid = request.form['regionid']
    scadavalue = float(request.form['scadavalue'])

    existing_battery = collection.find({"_id":_id})

    if existing_battery:
        for ex_battery in existing_battery:
            battery_scadavalue = float(ex_battery["scadavalue"])
       
            if scadavalue>battery_scadavalue:
                return f"Not enoght scadavalue to sell"
            else:
                balance_scadavalue = battery_scadavalue - scadavalue
                collection.find_one_and_update({"_id":_id}, {"$set": {"regionid": regionid, "scadavalue": balance_scadavalue}}, upsert=True)
                return redirect("/dischargeBattery")
    else:
        return f"{_id} not found"
