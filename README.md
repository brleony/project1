# Project 1

This website is part of my homework for the course Web Programming with Python and JavaScript.
The website allows you to create an account, to search for and check in to locations, and to see weather data.
It is also possible to query information via its API.

The website makes use of a database with tables for users, locations, locationnames and check ins.
The names of the locations have their own table because only 3835 of 7375 locationnames are unique (a city can have multiple zipcodes).

Folder "static" contains css and sassy css files. "Templates" contains the layout and html templates.
Application.py is the flask app.
Zips.csv contains the location data, that was imported in the database using import.py
Requirements.txt contains the Python packages that need to be installed in order to run the application.

Leony Brok