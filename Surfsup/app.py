# Import the dependencies.

from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session 
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save references to each table
Station = Base.classes.station
measurement= Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app= Flask (__name__)

@app.route('/')
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )



# Routes
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year from the last date in the dataset. Taken from previous code
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()

    # Convert the results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    station_data = session.query(Station.station, Station.name).all()

    # Convert the results to a list of dictionaries
    stations_list = [{'station': station, 'name': name} for station, name in station_data]

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    most_active_station_id = 'USC00519281'

    # Calculate the date one year from the last date in the dataset
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the previous year
    tobs_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station_id).\
        filter(measurement.date >= one_year_ago).all()

    # Convert the results to a list of dictionaries
    tobs_list = [{'date': date, 'temperature': temperature} for date, temperature in tobs_data]

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def temperature_start_date(start):
    # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    temperature_stats = session.query(
        func.min(measurement.tobs).label('min_temperature'),
        func.avg(measurement.tobs).label('avg_temperature'),
        func.max(measurement.tobs).label('max_temperature')
    ).filter(measurement.date >= start).all()

    temperature_stats_dict = {
        'start_date': start,
        'min_temperature': temperature_stats[0].min_temperature,
        'avg_temperature': temperature_stats[0].avg_temperature,
        'max_temperature': temperature_stats[0].max_temperature
    }

    return jsonify(temperature_stats_dict)

@app.route('/api/v1.0/<start>/<end>')
def temperature_start_end_date(start, end):
    # Calculate TMIN, TAVG, and TMAX for the specified date range
    temperature_stats = session.query(
        func.min(measurement.tobs).label('min_temperature'),
        func.avg(measurement.tobs).label('avg_temperature'),
        func.max(measurement.tobs).label('max_temperature')
    ).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Convert the results to a dictionary
    temperature_stats_dict = {
        'start_date': start,
        'end_date': end,
        'min_temperature': temperature_stats[0].min_temperature,
        'avg_temperature': temperature_stats[0].avg_temperature,
        'max_temperature': temperature_stats[0].max_temperature
    }

    return jsonify(temperature_stats_dict)

if __name__ == '__main__':
    app.run(debug=True)
