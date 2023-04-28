CREATE SCHEMA IF NOT EXISTS events;

CREATE TABLE events.types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE events.play_patterns (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE events.teams (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE events.positions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE events.players (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE events.events (
    id UUID PRIMARY KEY,
    index INTEGER NOT NULL,
    match_id TEXT NOT NULL,
    location_x FLOAT,
    location_y FLOAT,
    period INTEGER,
    timestamp FLOAT,
    minute INTEGER,
    second INTEGER,
    type_id INTEGER,
    position_id INTEGER,
    possession INTEGER,
    possession_team_id INTEGER,
    play_pattern_id INTEGER,
    team_id INTEGER,
    duration FLOAT,
    under_pressure BOOLEAN,
    off_camera BOOLEAN,
    out BOOLEAN,
    tactics_formation INTEGER,
    FOREIGN KEY (type_id) REFERENCES events.types(id),
    FOREIGN KEY (position_id) REFERENCES events.positions(id),
    FOREIGN KEY (possession_team_id) REFERENCES events.teams(id),
    FOREIGN KEY (play_pattern_id) REFERENCES events.play_patterns(id),
    FOREIGN KEY (team_id) REFERENCES events.teams(id)
);

CREATE TABLE events.related_events (
    event_id UUID NOT NULL,
    related_event_id UUID NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events.events(id),
    FOREIGN KEY (related_event_id) REFERENCES events.events(id)
);

CREATE TABLE events.lineups (
    event_id UUID NOT NULL,
    player_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    jersey_number INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events.events(id),
    FOREIGN KEY (player_id) REFERENCES events.players(id),
    FOREIGN KEY (position_id) REFERENCES events.positions(id),
);

    
CREATE INDEX idx_index ON events.events (index);
CREATE INDEX idx_timestamp ON events.events (timestamp);
CREATE INDEX idx_location_x ON events.events (location_x);
CREATE INDEX idx_location_y ON events.events (location_y);

ALTER TABLE IF EXISTS events.related_events
    ADD CONSTRAINT event_id_related_event_id UNIQUE (event_id, related_event_id);

SELECT *
FROM events.events
WHERE match_id = '267499'
AND event_index BETWEEN 1523 AND 1523
AND location_x BETWEEN 89 AND 90
AND location_y BETWEEN 70 AND 72;
