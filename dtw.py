import psycopg2
from fastdtw import fastdtw
import numpy as np
import time

COOR_THRESHOLD = 1
INDEX_THRESHOLD = 4
DISTANCE_THRSHOLD = 10

conn = psycopg2.connect(
    # host="0.tcp.ngrok.io",x
    # port=14396,
    host="localhost",
    database="main_db",
    user="root",
    password="root",
)


def euclidean_dist(x, y):
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def isSameLocation(l1, l2):
    return abs(l1[0] - l2[0]) <= COOR_THRESHOLD and abs(l1[1] - l2[1]) <= COOR_THRESHOLD


def isPotentialCandidate(candidate, targetPath=[]):
    targetPathLength = len(targetPath)
    matchId = candidate["match"]

    if not targetPathLength:
        return False

    limit = targetPathLength * INDEX_THRESHOLD

    cur = conn.cursor()

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

    cur.execute(query)
    locations = cur.fetchall()
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
    cur = conn.cursor()

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

    cur.execute(query)

    rows = cur.fetchall()

    # Convert the rows to a list of dictionaries
    result = [dict(zip(columns, row)) for row in rows]
    # for row in rows:
    #     print(row)
    # Close the cursor and database connection
    cur.close()

    return result


def getFullPath(candidate):
    cur = conn.cursor()

    query = """SELECT id, index, location_x, location_y
            FROM events.events
            WHERE match_id = '{}'
            AND index >= {}
            ORDER BY index ASC
            LIMIT 8
            """.format(
        candidate["match"], candidate["index"]
    )

    cur.execute(query)

    events = cur.fetchall()

    columns = ["id", "index", "location_x", "location_y"]

    events = [dict(zip(columns, event)) for event in events]

    return events


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
        locationXTuple=(targetX - COOR_THRESHOLD, targetX + COOR_THRESHOLD),
        locationYTuple=(targetY - COOR_THRESHOLD, targetY + COOR_THRESHOLD),
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
        print(distanceDict[candidate["eventId"]])
        result.append({"matchId": candidate["match"], "path": path})

    # print(result)
    return result


start_time = time.time()

paths = findPaths(targetPath=[(25,76), (27,36), (81,59), (43,4), (44,6)])
# paths = findPaths(
#     targetPath=[
#         (63.6, 3.1),
#         (57.4, 16.3),
#         (68, 3.3),
#         (57.3, 66.8),
#         (45.9, 11.5),
#         (52.8, 10.4),
#         (41.5, 23.9),
#         (41.5, 23.9),
#     ]
# )

# print paths
for pathDict in paths:
    path = pathDict["path"]
    print(pathDict["matchId"])
    finalPath = []
    for event in path:
        finalPath.append((event["location_x"], event["location_y"]))

    print(finalPath)

end_time = time.time()

print("Running time:", end_time - start_time, "seconds")

# getPoints(locationXTuple=(50,52),locationYTuple=(50,52), columns=["index","location_x","location_y","match_id"])

conn.close()
