# Creating a new database in PostgreSQL + Superset Apache

## Verify containers

`sudo docker ps`

If not, check:

```
cd ~/superset

sudo docker compose -f docker-compose-image-tag.yml up -d
```

## Run monitor_BIN.py
This should create a new database named beam_monitor.
Check *DAQ_PATH* and *CALIB_PATH*, and change them if necessary.

```
source beam_env/bin/activate
python monitor_BIN.py
```
where _beam_env_ is an environment that has the necessary libraries.

## Superset connection

* Open http://localhost:8088

* Create a new database connection: Settings -> Database Connections -> +Database -> PostgreSQL

* Host: localhost, Port: XXXX, Database: XXXX, user: XXXX, password: XXXX

**If** you can't connect through this port because it's marked as closed, try through SQLAlchemiURI.

-> Test Connection and then **Connect**

* Create datasets, one for each table (runs, histograms, cps)

## Superset Charts

Elaborate different charts depending on the information to draw. Line Charts is recommended for cps, relations and histograms data.
