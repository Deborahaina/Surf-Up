# -*- coding: utf-8 -*-
import numpy as np
#import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request



# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

#Create App routes
@app.route("/")
def welcome():

    # """List all available api routes."""
    return (
        f"Available Routes for climate analysis!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
#Find last date in database
    Last_Year_Observation = dt.date(2017, 8, 23) - dt.timedelta(days=7*52)

# Query all passengers

    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > Last_Year_Observation).all()

    precipitation= []
    for result in precipitation_results:
        row = {"date":"prcp"}
        row["date"] = result[0]
        row["prcp"] = float(result[1])
        precipitation.append(row)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")

def stationName():
    # Query all station names
    stationName_results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stationName_list = list(np.ravel(stationName_results))

    # Jsonify all_tobs
    return jsonify(stationName_list)

# Return a JSON list of Temperature Observations (tobs) for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    #Find last date in database
    Last_Year_Observation = dt.date(2017, 8, 23) - dt.timedelta(days=7*52)

    Last_Year_Observation

    # Query temp observations
    tobs_results = session.query(Measurement.tobs).filter(Measurement.date > Last_Year_Observation).all()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_results))

    # Jsonify all_tobs
    return jsonify(tobs_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<startdate>")
def start_date(startdate):
    #Parse the date 
    St_Date = dt.datetime.strptime(startdate,"%Y-%m-%d")

    # Calculate summary stats
    summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date >= St_Date).all()

    summary = list(np.ravel(summary_stats))

    # Jsonify summary
    return jsonify(summary)

# Same as above but this time with an end Date
@app.route("/api/v1.0/<startdate>/<enddate>")
def daterange(startdate,enddate):
    #Parse the date 
    Start_Date = dt.datetime.strptime(startdate,"%Y-%m-%d")
    End_Date = dt.datetime.strptime(enddate,"%Y-%m-%d")

    # Calculate summary stats
    summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date.between(Start_Date,End_Date)).all()
    
    summary = list(np.ravel(summary_stats))

    # Jsonify summary
    return jsonify(summary)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)





