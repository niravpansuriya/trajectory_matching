from dotenv import load_dotenv

load_dotenv()

import psycopg2
from fastdtw import fastdtw
import numpy as np
import time
import os

DISTANCE_MARGIN = 1
DISTANCE_THRSHOLD = 10
PATH_LENGTH = 10

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


def euclidean_dist(x, y):
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def isSameLocation(l1, l2):
    return (
        abs(l1[0] - l2[0]) <= DISTANCE_MARGIN and abs(l1[1] - l2[1]) <= DISTANCE_MARGIN
    )


def isPotentialCandidate(candidate, targetPath=[]):
    targetPathLength = len(targetPath)
    matchId = candidate["match"]

    if not targetPathLength:
        return False

    limit = targetPathLength * 4

    # get all points till the limit starting from the candidate

    query = """SELECT location_x, location_y
        FROM events.events
        WHERE match_id = '{}'
        AND index >= {}
        ORDER BY index ASC
        LIMIT {};
        """.format(
        matchId, candidate["index"], limit
    )

    cursor.execute(query)
    locations = cursor.fetchall()
    nonNullLocations = []
    minDistance = float("inf")
    for i in range(len(locations)):
        location = locations[i]
        # if location[0] and location[1] and isSameLocation(targetPath[-1], location):
        if location[0] and location[1]:
            nonNullLocations.append(location)
            distance, _ = fastdtw(nonNullLocations, targetPath, dist=euclidean_dist)
            minDistance = min(minDistance, distance)
            if distance <= DISTANCE_THRSHOLD:
                return (True, minDistance)

    return (False, minDistance)


def getPoints(
    matchId=None, indexTuple=(), locationXTuple=(), locationYTuple=(), columns=[]
):
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
    for event in events:
        path.append((event["location_x"], event["location_y"]))
    return path


def getTopFive(candidates, distanceDict):
    candidatesWithDistance = []

    for candidate in candidates:
        candidatesWithDistance.append(
            {"distance": distanceDict[candidate["eventId"]], "candidate": candidate}
        )

    sortedCandidates = sorted(candidatesWithDistance, key=lambda x: x["distance"])

    result = []
    for ele in sortedCandidates[:5]:
        result.append(ele["candidate"])

    return result


def findPaths(targetPath=[]):
    candidates = []
    targetX = targetPath[0][0]
    targetY = targetPath[0][1]
    points = getPoints(
        locationXTuple=(targetX - DISTANCE_MARGIN, targetX + DISTANCE_MARGIN),
        locationYTuple=(targetY - DISTANCE_MARGIN, targetY + DISTANCE_MARGIN),
        columns=["id", "match_id", "index", "location_x", "location_y"],
    )

    for p in points:
        candidates.append(
            {
                "eventId": p["id"],
                "index": p["index"],
                "match": p["match_id"],
            }
        )

    potentialCandidates = []
    distanceDict = dict()

    for candidate in candidates:
        # if isPotentialCandidate(candidate, targetPath)[0]:
        distance = isPotentialCandidate(candidate, targetPath)[1]
        distanceDict[candidate["eventId"]] = distance
        potentialCandidates.append(candidate)

    candidateDict = dict()

    for candidate in potentialCandidates:
        match = candidate["match"]
        if match in candidateDict:
            if candidateDict[match]["index"] > candidate["index"]:
                candidateDict[match] = candidate
        else:
            candidateDict[match] = candidate

    candidates = list(candidateDict.values())
    topFiveCandidates = getTopFive(candidates=candidates, distanceDict=distanceDict)

    result = []
    for candidate in topFiveCandidates:
        path = getFullPath(candidate)
        result.append({"matchId": candidate["match"], "path": path})

    return result


def main():
    connect_db()
    paths = findPaths(targetPath=targetPath)
    
    for path in paths:
        print(path)

    cursor.close()
    dbObj.close()

if __name__ == '__main__':
    start_time = time.time()

    main()

    end_time = time.time()

    print("Running time:", end_time - start_time, "seconds")
