CREATE TABLE IF NOT EXISTS Dim_Artists (
    artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name TEXT UNIQUE NOT NULL,
    primary_genre TEXT DEFAULT 'Music'
);

CREATE TABLE IF NOT EXISTS Dim_Videos (
    video_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name TEXT,
    video_title TEXT NOT NULL,
    release_date TEXT,
    FOREIGN KEY (artist_name) REFERENCES Dim_Artists(artist_name)
);

CREATE TABLE IF NOT EXISTS Dim_Platforms (
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT UNIQUE NOT NULL,
    syndicate_type TEXT
);

CREATE TABLE IF NOT EXISTS Fact_Video_Metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_title TEXT,
    platform_id INTEGER,
    view_count BIGINT DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    playback_errors INTEGER DEFAULT 0,
    satisfaction_rate REAL DEFAULT 100.0,
    FOREIGN KEY (platform_id) REFERENCES Dim_Platforms(platform_id)
);