import json
import os
import psycopg2
from psycopg2.extras import execute_values


def upsertData(data):
    upsert_query = """INSERT INTO events.events (match_id, event_index, timestamp, location_x, location_y) VALUES %s 
                      ON CONFLICT (match_id, event_index) 
                      DO UPDATE SET 
                      timestamp = EXCLUDED.timestamp, 
                      location_x = EXCLUDED.location_x, 
                      location_y = EXCLUDED.location_y"""

    # Insert data using batch processing
    with conn.cursor() as cur:
        execute_values(cur, upsert_query, data)

    # Commit the changes to the database
    conn.commit()


def getDataBatch(filePath, matchId):
    data = []
    with open(filePath, "r") as f:
        jsonData = json.load(f)

        for row in jsonData:
            if "location" in row:
                data.append(
                    (
                        matchId,
                        row["index"],
                        get_seconds(row["timestamp"]),
                        row["location"][0],
                        row["location"][1],
                    )
                )
    return data


def get_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.split(":"))
    return seconds + 60 * minutes + 3600 * hours


conn = psycopg2.connect(
    # host="0.tcp.ngrok.io",
    # port=14396,
    host="localhost",
    database="main_db",
    user="root",
    password="root",
)


# get file names
files = os.listdir("./data")

for fileName in files:
    print(fileName)

    # get data
    data = getDataBatch("./data/{}".format(fileName), fileName.split(".")[0])
    upsertData(data)


# Close the database connection
conn.close()
