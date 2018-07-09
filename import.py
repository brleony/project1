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
    datareader = csv.reader(csvfile)

    location_names = set()

    # Print rows.
    for row in datareader:
        location_names.add(row[1] + ', ' + row[2])

    print(len(location_names))

# db.execute()