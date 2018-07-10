# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# import.py
#
# Web Programming with Python and Javascript
# Leony Brok
#
# Takes information from a csv with US ZIP codes and imports it into a PostgreSQL database.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

uri = "postgres://qxnbzedrqzofdu:40b192e433796771fa16f5d7835d6df4261d7ba4a840f140706c92128f00f797@ec2-54-163-236-188.compute-1.amazonaws.com:5432/da9pe39dr3uasb"

# Set up database
engine = create_engine(uri)
db = scoped_session(sessionmaker(bind=engine))

# Open csv with zip codes.
with open('zips.csv', newline='') as csvfile:

    datareader = csv.DictReader(csvfile)

    # TODO
    for i, row in enumerate(datareader):

        db.execute(
            "DO $$"
                " BEGIN INSERT INTO locationnames (city, state) VALUES (:city, :state);"
                " EXCEPTION WHEN unique_violation THEN RAISE NOTICE 'row skipped';"
            " END; $$",
            {"city": row["City"], "state": row["State"]})

        locationname_id = db.execute("SELECT locationname_id FROM locationnames WHERE city = :city AND state = :state",
            {"city": row["City"], "state": row["State"]}).fetchone()

        db.execute("INSERT INTO locations (zipcode, locationname_id, latitude, longitude, population) VALUES (:zipcode, :locationname_id, :latitude, :longitude, :population)",
            {"zipcode": row["Zipcode"], "locationname_id": locationname_id[0], "latitude": row["Lat"], "longitude": row["Long"], "population": row["Population"]})

        print(i, row["Zipcode"])

    # Commit to database.
    db.commit()