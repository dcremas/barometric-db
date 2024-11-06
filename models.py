import os
import psycopg2
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv('PG_DB')
user = os.getenv('PG_USERNAME')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
port =os.getenv('PG_PORT')

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
SELECT loc.station_name, hf.time, hf.pressure_in, tz.utc_offset
FROM locations loc
JOIN hourlyforecasts hf
    ON loc.station = hf.station
JOIN regions rg
    ON loc.state = rg.state
JOIN time_zones tz
    ON rg.tz_abbreviation = tz.abbreviation
ORDER BY loc.station_name, hf.time;
'''

query_data_slp = '''
SELECT *
FROM hf_baro_impact
WHERE slp_3hr_diff BETWEEN -5.0 AND -0.15
    OR slp_6hr_diff BETWEEN -5.0 AND -0.25
    OR slp_24hr_diff BETWEEN -5.0 AND -0.50
ORDER BY station, slp_3hr_diff;
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
    data = list(map(lambda x: (x[0], x[1] + timedelta(hours = x[3]), x[2]), data))
    cursor.execute(query_data_slp)
    response_data_slp = cursor.fetchall()
    data_slp = [x for x in response_data_slp]
    data_slp = list(map(lambda x: (x[0], x[1], x[2], x[3], x[4], x[5] + timedelta(hours = x[13]), x[6], x[7], x[8], x[9], x[10], x[11], x[12]), data_slp))
    cursor.execute(query_update)
    response_update = cursor.fetchall()
    update = response_update[0][0]
    update = (update - timedelta(hours = 6))
    
headers = ['station_name', 'time', 'pressure_in']
