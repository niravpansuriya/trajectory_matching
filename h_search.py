import psycopg2

COOR_THRESHOLD = 0.5
INDEX_THRESHOLD = 3

conn = psycopg2.connect(
    # host="0.tcp.ngrok.io",
    # port=14396,
    host="localhost",
    database="main_db",
    user="root",
    password="root",
)


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


def findPaths(targetPath=[]):
    candidates = []
    isFirst = True

    for targetCoor in targetPath:
        if isFirst:
            targetX = targetCoor[0]
            targetY = targetCoor[1]
            points = getPoints(
                locationXTuple=(targetX - COOR_THRESHOLD, targetX + COOR_THRESHOLD),
                locationYTuple=(targetY - COOR_THRESHOLD, targetY + COOR_THRESHOLD),
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
                    indexTuple=(curr["index"] + 1, curr["index"] + INDEX_THRESHOLD),
                    locationXTuple=(
                        targetX - COOR_THRESHOLD,
                        targetX + COOR_THRESHOLD,
                    ),
                    locationYTuple=(
                        targetY - COOR_THRESHOLD,
                        targetY + COOR_THRESHOLD,
                    ),
                    columns=["id","match_id", "index", "location_x", "location_y"],
                )

                if len(points) == 0:
                    # remove the element
                    # candidates.remove(i)
                    # del candidates[i]
                    # i -= 1
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

    # print(candidates)
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

    # print(result)
    return result


paths = findPaths(targetPath=[(25,76), (27,36), (81,59), (43,4), (44,6)])

l = []
for p in paths:
    path = p["path"]
    for ele in path:
        l.append((ele["location_x"], ele["location_y"]))
print(l)
# getPoints(locationXTuple=(50,52),locationYTuple=(50,52), columns=["index","location_x","location_y","match_id"])

conn.close()
