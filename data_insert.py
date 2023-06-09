from dotenv import load_dotenv
load_dotenv()
import json
import os
import psycopg2
from psycopg2.extras import execute_values

# global variables
dbObj = None
cursor = None

# returns filenames of datafile inside data folder
def getFileNames(directory):
    for filename in os.listdir(directory):
        # Check if the item is a file (not a directory)
        if os.path.isfile(os.path.join(directory, filename)):
            yield filename


# read json data from data file
def getData(directory, filename):
    with open(directory + "/" + filename, "r") as f:
        data = json.load(f)
        return data

# connect with database
# setup global dbObj and cursor variable
def connect_db():
    global dbObj, cursor
    dbObj = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
    )
    cursor = dbObj.cursor()

# convert timestamp string to seconds
def get_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.split(":"))
    return seconds + 60 * minutes + 3600 * hours

"""
SQL generator methods
These methods will generate insertion query for each table
"""
def generateEventInsertQuery():
    columns = [
        "id",
        "index",
        "match_id",
        "location_x",
        "location_y",
        "period",
        "timestamp",
        "minute",
        "second",
        "type_id",
        "possession",
        "possession_team_id",
        "play_pattern_id",
        "team_id",
        "position_id",
        "duration",
        "under_pressure",
        "off_camera",
        "out",
        "tactics_formation",
    ]

    placeholders = ", ".join(["%s" for _ in columns])

    updates = ", ".join([f"{column} = EXCLUDED.{column}" for column in columns])

    query = f"""
        INSERT INTO events.events ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (id)
        DO UPDATE SET {updates};
    """

    return query


def generateTypesInsertQuery():
    query = f"""
        INSERT INTO events.types (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name;
    """
    return query


def generatePlayPatternsInsertQuery():
    query = f"""
        INSERT INTO events.play_patterns (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name;
    """
    return query


def generateTeamsInsertQuery():
    query = f"""
        INSERT INTO events.teams (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name;
    """
    return query


def generatePositionsInsertQuery():
    query = f"""
        INSERT INTO events.positions (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name;
    """
    return query


def generatePlayersInsertQuery():
    query = f"""
        INSERT INTO events.players (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name;
    """
    return query


def generateLineupsInsertQuery():
    columns = ["event_id", "player_id", "position_id", "jersey_number"]

    placeholders = ", ".join(["%s" for _ in columns])

    updates = ", ".join([f"{column} = EXCLUDED.{column}" for column in columns])

    query = f"""
        INSERT INTO events.lineups ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (event_id, player_id) 
        DO UPDATE SET {updates};
    """
    return query


def generateRelatedEventsInsertQuery():
    columns = ["event_id", "related_event_id"]

    placeholders = ", ".join(["%s" for _ in columns])

    updates = ", ".join([f"{column} = EXCLUDED.{column}" for column in columns])

    query = f"""
        INSERT INTO events.related_events ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (event_id, related_event_id) 
        DO UPDATE SET {updates};
    """
    return query

"""
These methods will convert json data to values which
can be inserted in database
"""

def getEvent(data, match_id):
    values = []
    for obj in data:
        values.append(
            (
                obj.get("id"),
                obj.get("index"),
                match_id,
                obj.get("location", [None, None])[0],
                obj.get("location", [None, None])[1],
                obj.get("period"),
                get_seconds(obj.get("timestamp")),
                obj.get("minute"),
                obj.get("second"),
                obj.get("type", {}).get("id"),
                obj.get("possession"),
                obj.get("possession_team", {}).get("id"),
                obj.get("play_pattern", {}).get("id"),
                obj.get("team", {}).get("id"),
                obj.get("position", {}).get("id"),
                obj.get("duration"),
                obj.get("under_pressure"),
                obj.get("off_camera"),
                obj.get("out"),
                obj.get("tactics", {}).get("formation"),
            )
        )
    return values


def getTypes(data):
    values = set()
    for obj in data:
        if "type" in obj:
            values.add(
                (
                    obj.get("type", {}).get("id"),
                    obj.get("type", {}).get("name"),
                )
            )
    return list(values)


def getPlayPatterns(data):
    values = set()
    for obj in data:
        if "play_pattern" in obj:
            values.add(
                (
                    obj.get("play_pattern", {}).get("id"),
                    obj.get("play_pattern", {}).get("name"),
                )
            )
    return list(values)


def getTeams(data):
    values = set()
    for obj in data:
        if "team" in obj:
            values.add(
                (
                    obj.get("team", {}).get("id"),
                    obj.get("team", {}).get("name"),
                )
            )
    return list(values)


def getPositions(data):
    values = set()
    for obj in data:
        if "position" in obj:
            values.add(
                (
                    obj.get("position", {}).get("id"),
                    obj.get("position", {}).get("name"),
                )
            )
    return list(values)


def getPlayers(data):
    values = set()
    for obj in data:
        if "player" in obj:
            values.add(
                (
                    obj.get("player", {}).get("id"),
                    obj.get("player", {}).get("name"),
                )
            )
        if "tactics" in obj  and "lineup" in obj["tactics"]:
            for lineup in obj["tactics"]["lineup"]:
                values.add(
                (
                    lineup.get("player", {}).get("id"),
                    lineup.get("player", {}).get("name"),
                )
            )

    return list(values)


def getLineUps(data):
    values = []
    for obj in data:
        if "tactics" in obj and "lineup" in obj["tactics"]:
            for lineup in obj["tactics"]["lineup"]:
                values.append(
                    (
                        obj.get("id"),
                        lineup["player"]["id"],
                        lineup["position"]["id"],
                        lineup["jersey_number"],
                    )
                )
    return values


def getRelatedEvents(data):
    values = []
    for obj in data:
        if "related_events" in obj:
            for relatedEventId in obj["related_events"]:
                values.append((obj["id"], relatedEventId))
    return values


# execute batch query
def executeBatchInsert(query, values):
    try:
        # Execute the batch queries
        cursor.executemany(query, values)

    except Exception as e:
        raise e


def main():
    # connect the database
    connect_db()
    
    # for every data file
    for filename in getFileNames("./data"):
        
        # read data from file
        data = getData("./data", filename)

        # get match id from filename
        match_id = filename.replace(".json","").strip()
        print(f"{filename} started")

        # try to to insert data in every table with batch insert
        try:
            executeBatchInsert(generateTypesInsertQuery(), getTypes(data))
            executeBatchInsert(generatePlayPatternsInsertQuery(), getPlayPatterns(data))
            executeBatchInsert(generateTeamsInsertQuery(), getTeams(data))
            executeBatchInsert(generatePositionsInsertQuery(), getPositions(data))
            executeBatchInsert(generatePlayersInsertQuery(), getPlayers(data))
            executeBatchInsert(generateEventInsertQuery(), getEvent(data, match_id))
            executeBatchInsert(generateRelatedEventsInsertQuery(), getRelatedEvents(data))
            executeBatchInsert(generateLineupsInsertQuery(), getLineUps(data))

        # if any error then rollback the transaction
        except Exception as e:
            # If there is an error, rollback the transaction
            dbObj.rollback()
            print(f"Error executing batch queries: {e}")

        # if insertion successful for the match
        # then commit the transaction
        # else rollback
        try:
            dbObj.commit()
        except Exception as e:
            dbObj.rollback()
            print(f"Error executing batch queries: {e}")
    
    # at the end close the cursor and database connection
    cursor.close()
    dbObj.close()

if __name__ == '__main__':
    main()