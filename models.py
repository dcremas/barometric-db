import psycopg2
from datetime import timedelta

dbname = 'apple_weatherkit'
user = 'dustincremascoli'
password = 'mp2BrVcin8chgfxUO7vb'
host = 'db-aws.cu1h5zzynwdo.us-east-2.rds.amazonaws.com'
port = 5432

query_airports = f'''
SELECT DISTINCT loc.station_name
FROM locations loc
JOIN hourlyforecasts hf
    ON loc.station = hf.station
JOIN regions rg
    ON loc.state = rg.state
ORDER BY loc.station_name;
'''

query_data = f'''
SELECT loc.station_name, hf.time, hf.pressure_in
FROM locations loc
JOIN hourlyforecasts hf
    ON loc.station = hf.station
JOIN regions rg
    ON loc.state = rg.state
ORDER BY loc.station_name, hf.time;
'''

query_update = f'''
SELECT
MAX(timestamp)
FROM hourlyforecasts;
'''

url_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

with psycopg2.connect(url_string) as connection:
    cursor = connection.cursor()
    cursor.execute(query_airports)
    response_airports = cursor.fetchall()
    airports = [x[0] for x in response_airports]
    cursor.execute(query_data)
    response_data = cursor.fetchall()
    data = [x for x in response_data]
    cursor.execute(query_update)
    response_update = cursor.fetchall()
    update = response_update[0][0]
    update = (update - timedelta(hours = 6))
    
headers = ['station_name', 'time', 'pressure_in']
