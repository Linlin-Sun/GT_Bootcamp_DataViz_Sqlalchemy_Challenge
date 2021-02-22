from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy as sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

app = Flask(__name__)

engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args = {'check_same_thread': False})
session = Session(bind = engine)
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

latest_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
latest_date = dt.datetime.strptime(latest_date_str, '%Y-%m-%d')
one_year_ago_date = latest_date - dt.timedelta(days = 365)

@app.route('/')
def index():
    return ('Usage of this website:<br>'
    '/api/v1.0/precipitation<br>'
    '/api/v1.0/stations<br>'
    '/api/v1.0/tobs<br>'
    '/api/v1.0/&lt;start&gt;<br>'
    '/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>'
    )
    
@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()
    prec = {result[0]:result[1] for result in results}
    return jsonify(prec)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    final_result = list(np.ravel(results))
    return jsonify(stations = final_result)

@app.route('/api/v1.0/tobs')
def tobs():
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date > one_year_ago_date).all()
    final_result = list(np.ravel(results))
    return jsonify(stations = final_result)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end = None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date > start).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
if __name__ == '__main__':
    app.run(debug = True)