CREATE SCHEMA IF NOT EXISTS events;

CREATE TABLE IF NOT EXISTS events.types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events.play_patterns (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events.teams (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events.positions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events.players (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events.events (
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

CREATE TABLE IF NOT EXISTS events.related_events (
    event_id UUID NOT NULL,
    related_event_id UUID NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events.events(id),
    FOREIGN KEY (related_event_id) REFERENCES events.events(id)
);

CREATE TABLE IF NOT EXISTS events.lineups (
    event_id UUID NOT NULL,
    player_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    jersey_number INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events.events(id),
    FOREIGN KEY (player_id) REFERENCES events.players(id),
    FOREIGN KEY (position_id) REFERENCES events.positions(id)
);

    
CREATE INDEX IF NOT EXISTS idx_index ON events.events (index);
CREATE INDEX IF NOT EXISTS idx_timestamp ON events.events (timestamp);
CREATE INDEX IF NOT EXISTS idx_match_id ON events.events (match_id);
CREATE INDEX IF NOT EXISTS idx_location_x ON events.events (location_x);
CREATE INDEX IF NOT EXISTS idx_location_y ON events.events (location_y);

ALTER TABLE IF EXISTS events.related_events
    ADD CONSTRAINT event_id_related_event_id UNIQUE (event_id, related_event_id);

ALTER TABLE IF EXISTS events.lineups
    ADD CONSTRAINT event_id_player_id UNIQUE (event_id, player_id);
