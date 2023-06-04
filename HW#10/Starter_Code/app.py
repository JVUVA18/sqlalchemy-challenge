# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, Column, Integer, String, desc, distinct
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine, reflect = True)
Measures = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Welcome to the weather app. Use the routes below to access data held within our database."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/enter_start_date (YYYY-MM-DD)<br/>"
        f"/api/v1.0/enter_start_date (YYYY-MM-DD)/enter_end_date (YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(func.max(Measures.date)).scalar()
    prev_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=366)
    results = session.query(Measures.date, Measures.prcp).filter(Measures.date >= prev_year)
    session.close()
    rain_year = []
    for dat, prec in results:
        rain_dict = {}
        rain_dict[dat] = prec
        rain_year.append(rain_dict)
    
    return jsonify(rain_year)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    all_stations = []
    for sta, nam, lat, lon, ele in results:
        sta_dict = {}
        sta_dict[sta] = nam 
        sta_dict['latitude'] = lat
        sta_dict['longitude'] = lon
        sta_dict['elevation'] = ele
        all_stations.append(sta_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(func.max(Measures.date)).scalar()
    prev_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=366)
    unique_counts = session.query(Measures.station, func.count(Measures.station)).\
                    group_by(Measures.station).order_by(desc(func.count(Measures.station))).all()
    most_active = unique_counts[0][0]
    results = session.query(Measures.tobs, Measures.date).filter(Measures.station == most_active).filter(Measures.date >= prev_year).all()
    session.close()
    year_tobs = []
    for tob, dat in results:
        tob_dict = {}
        tob_dict[dat] = tob
        year_tobs.append(tob_dict)
        
    return jsonify(year_tobs)
 
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(Measures.tobs), func.max(Measures.tobs), func.avg(Measures.tobs))\
              .filter(Measures.date >= start).all()
    sumstats = []
    for mi, ma, av in results:
        sumdict = {}
        sumdict['min temp'] = mi
        sumdict['max temp'] = ma
        sumdict['average temp'] = av
        sumstats.append(sumdict)
    
    return jsonify(sumstats)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    results = session.query(func.min(Measures.tobs), func.max(Measures.tobs), func.avg(Measures.tobs))\
        .filter(Measures.date >= start).filter(Measures.date <= end).all()
    sumstats = []
    for mi, ma, av in results:
        sumdict = {}
        sumdict['min temp'] = mi
        sumdict['max temp'] = ma
        sumdict['average temp'] = av
        sumstats.append(sumdict)
    
    return jsonify(sumstats)

if __name__ == '__main__':
    app.run(debug=True)
