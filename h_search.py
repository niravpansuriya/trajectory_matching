from dotenv import load_dotenv

load_dotenv()

import psycopg2
import os
import time

# define constants
DISTANCE_MARGIN = 1  # gives flexibility to match location
EVENTS_LOOKUP_THRESHOLD = 3  # makes algorithm flexible
PATH_LENGTH = 10  # length of the matched paths

# global variables
dbObj = None
cursor = None
targetPath = [(25, 76), (27, 36), (81, 59), (43, 4), (44, 6)]

# connect with database
# setup global dbObj and cursor variable
def connect_db():
    global dbObj, cursor
    dbObj = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    cursor = dbObj.cursor()


""" get points of given match id,
    with index between(lower_index, higher_index),
    with location in given range
    it will return data of provided columns
"""
def getPoints(
    matchId=None, indexTuple=(), locationXTuple=(), locationYTuple=(), columns=[]
):
    # cur = conn.cursor()

    if not len(columns):
        return []

    colString = ",".join(columns)

    if matchId:
        query = """SELECT {}
            FROM events.events
            WHERE match_id = '{}'
            AND index BETWEEN {} AND {}
            AND location_x BETWEEN {} AND {}
            AND location_y BETWEEN {} AND {};""".format(
            colString,
            matchId,
            indexTuple[0],
            indexTuple[1],
            locationXTuple[0],
            locationXTuple[1],
            locationYTuple[0],
            locationYTuple[1],
        )
    else:
        query = """SELECT {}
            FROM events.events
            WHERE location_x BETWEEN {} AND {}
            AND location_y BETWEEN {} AND {};""".format(
            colString,
            locationXTuple[0],
            locationXTuple[1],
            locationYTuple[0],
            locationYTuple[1],
        )

    cursor.execute(query)

    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    result = [dict(zip(columns, row)) for row in rows]

    return result

# get path of length PATH_LENGTH starting from given candidate
def getFullPath(candidate):

    query = """SELECT location_x, location_y
            FROM events.events
            WHERE match_id = '{}'
            AND index >= {}
            ORDER BY index ASC
            LIMIT {}
            """.format(
        candidate["match"], candidate["index"], PATH_LENGTH
    )

    cursor.execute(query)

    events = cursor.fetchall()

    columns = ["location_x", "location_y"]

    events = [dict(zip(columns, event)) for event in events]

    path = []
    for candidate in events:
        path.append((candidate["location_x"], candidate["location_y"]))

    return path

def findPaths(targetPath=[]):
    candidates = []
    isFirst = True

    for targetCoor in targetPath:
        if isFirst:
            targetX = targetCoor[0]
            targetY = targetCoor[1]
            points = getPoints(
                locationXTuple=(targetX - DISTANCE_MARGIN, targetX + DISTANCE_MARGIN),
                locationYTuple=(targetY - DISTANCE_MARGIN, targetY + DISTANCE_MARGIN),
                columns=["id", "match_id", "index", "location_x", "location_y"],
            )

            for p in points:
                candidates.append(
                    {
                        "start_point": {
                            "eventId": p["id"],
                            "index": p["index"],
                            "match": p["match_id"],
                        },
                        "curr_point": {
                            "eventId": p["id"],
                            "index": p["index"],
                            "match": p["match_id"],
                            "location": (p["location_x"], p["location_y"]),
                        },
                    }
                )
            isFirst = False

        else:
            removedIndexes = []
            for i in range(len(candidates)):
                candidate = candidates[i]
                curr = candidate["curr_point"]
                targetX = targetCoor[0]
                targetY = targetCoor[1]
                points = getPoints(
                    matchId=curr["match"],
                    indexTuple=(
                        curr["index"] + 1,
                        curr["index"] + EVENTS_LOOKUP_THRESHOLD,
                    ),
                    locationXTuple=(
                        targetX - DISTANCE_MARGIN,
                        targetX + DISTANCE_MARGIN,
                    ),
                    locationYTuple=(
                        targetY - DISTANCE_MARGIN,
                        targetY + DISTANCE_MARGIN,
                    ),
                    columns=["id", "match_id", "index", "location_x", "location_y"],
                )

                if len(points) == 0:
                    removedIndexes.append(i)

                else:
                    t = points[0]
                    curr["eventId"] = t["id"]
                    curr["index"] = t["index"]
                    curr["match"] = t["match_id"]
                    curr["location"] = (t["location_x"], t["location_y"])

            candidates = [
                candidates[i] for i in range(len(candidates)) if i not in removedIndexes
            ]

   
    # remove candidates from the same match
    candidateDict = dict()

    for candidate in candidates:
        match = candidate["start_point"]["match"]
        if match in candidateDict:
            if candidateDict[match]["index"] > candidate["start_point"]["index"]:
                candidateDict[match] = candidate["start_point"]
        else:
            candidateDict[match] = candidate["start_point"]

    result = []
    for matchId in candidateDict.keys():
        path = getFullPath(candidateDict[matchId])
        result.append({"matchId": matchId, "path": path})

    return result

def main():
    connect_db()

    paths = findPaths(targetPath=targetPath)
    print(paths)

    cursor.close()
    dbObj.close()

if __name__ == '__main__':
    start_time = time.time()

    main()

    end_time = time.time()

    print("Running time:", end_time - start_time, "seconds")

