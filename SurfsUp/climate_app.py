# Import the dependencies.
import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaiian Climate API <br/>"
        f"Please browse the follwing routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        
        f"<p> Please query 'start' and 'end' dates in the following format: MMDDYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
#Return the precipitation data for the last year
# Calculate the date 1 year ago from last date in database

    past_year_precip = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= past_year_precip).all()
    
    session.close()

    precip = []
    for prcp, date in precip:
        precip_dict = {}
        precip_dict["precipitation"] = prcp
        precip_dict["date"] = date
        precip.append(precip_dict)
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
# Return a list of stations.
    
    session = Session(engine)
    station_query = session.query(Station.station).all()

    session.close()

#Unravel results into array/list
    stations = list(np.ravel(station_query))
    return jsonify(stations=stations)

# Return temps (tobs) for past 12 months
@app.route("/api/v1.0/tobs")
def temps():
    
    session = Session(engine)
    past_year_precip = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Search for primary station for tobs from past 12 months

    primary_station_temps = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= past_year_precip).all()
        
    session.close()

# Unravel
    temperature = list(np.ravel(primary_station_temps))
    return jsonify(temperature=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def date_stats(start=None, end=None):
    
# Find min, max and average temps from specific date   
    session = Session(engine)
    temp_stats = [func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        
        query_result = session.query(*temp_stats).\
            filter(Measurement.date >= start).all()
            
        session.close()
        
        temperature = list(np.ravel(query_result))
        return jsonify(temperature)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    query_result = session.query(*temp_stats).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    session.close()
    
if __name__ == '__main__':
    app.run()