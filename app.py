# ============================================================================
# DUAL-SOURCE DATA ACQUISITION & INTEGRATION PIPELINE
# ----------------------------------------------------------------------------
# Source 1: Trending YouTube Video Statistics (US Region)
# URL: https://www.kaggle.com/datasets/datasnaek/youtube-new
#
# Source 2: Spotify Tracks Dataset (Artist Metadata & Track Features)
# URL: https://kaggle.com
# ============================================================================

import os
import sqlite3
import pandas as pd

# Define paths within your VS Code project workspace
DB_PATH = "video_syndicate.db"
YOUTUBE_CSV = os.path.join("data", "USvideos.csv")
SPOTIFY_CSV = os.path.join("data", "spotify_tracks.csv")
SCHEMA_PATH = "schema.sql"

def run_integrated_pipeline():
    # 1. Operational Verification Check: Ensure both raw data files are in position
    if not os.path.exists(YOUTUBE_CSV) or not os.path.exists(SPOTIFY_CSV):
        print("Error: Missing required raw data architecture target files inside 'data/' folder.")
        print(f"Please verify that both '{YOUTUBE_CSV}' and '{SPOTIFY_CSV}' are present in your workspace.")
        return

    print("Connecting to local SQLite engine...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Database Initialization: Initialize tables using your schema blueprint
    print("Building relational structure from schema.sql...")
    with open(SCHEMA_PATH, "r") as schema_file:
        cursor.executescript(schema_file.read())
    conn.commit()

    # Seed core distribution platforms cleanly
    cursor.executescript("""
        INSERT OR IGNORE INTO Dim_Platforms (platform_name, syndicate_type) 
        VALUES ('YouTube', 'Standard Ad-Supported'), ('Qybe', 'Premium Closed Syndicate');
    """)
    conn.commit()

    # 3. Extraction Phase: Ingest large data logs using Pandas
    print("Extracting records from Source 1: YouTube Log Dumps...")
    yt_cols = ['title', 'channel_title', 'publish_time', 'views', 'likes', 'comment_count']
    yt_df = pd.read_csv(YOUTUBE_CSV, usecols=yt_cols).dropna(subset=['title', 'channel_title'])
    
    # Transformation Phase: Strip out corrupted or missing rows
    print("Scrubbing anomalies from YouTube data elements...")
    yt_df = yt_df[(yt_df['views'] >= 0) & (yt_df['likes'] >= 0)]
    clean_yt_records = yt_df.head(2500)

    print("Extracting dimensions from Source 2: Spotify Tracks Dataset...")
    spot_cols = ['artists', 'track_genre', 'popularity']
    spot_df = pd.read_csv(SPOTIFY_CSV, usecols=spot_cols).dropna(subset=['artists'])

    # 4. Data Processing Layer: Group, clean, and isolate unique Spotify artist metrics
    print("Normalizing multi-source metadata entities into dimensional attributes...")
    # Clean up bracket notation often found in raw Spotify artist lists
    spot_df['artists'] = spot_df['artists'].str.replace(r"[\[\]']", "", regex=True)
    
    artist_metadata = spot_df.groupby('artists').agg({
        'track_genre': 'first',
        'popularity': 'max'
    }).reset_index()

    # Construct a high-performance hash dictionary for lightning-fast relational data mapping
    spotify_lookup = {
        row['artists'].lower().strip(): (row['track_genre'], int(row['popularity']))
        for _, row in artist_metadata.iterrows()
    }

    # 5. Load Phase: Safely transfer elements into structural database tables
    print("Loading unified layers into normalized database layout...")
    
    # Fetch platform IDs for our relational link keys
    cursor.execute("SELECT platform_id FROM Dim_Platforms WHERE platform_name = 'YouTube'")
    youtube_id = cursor.fetchone()[0]

    for _, row in clean_yt_records.iterrows():
        channel_name = row['channel_title']
        channel_lookup_key = channel_name.lower().strip()

        # Check if we have matching artist data from Spotify, otherwise assign generic fallbacks
        if channel_lookup_key in spotify_lookup:
            genre, popularity = spotify_lookup[channel_lookup_key]
        else:
            genre, popularity = "Music/Trending", 50

        # Inject artist dimensions into lookup maps securely, passing your new popularity column
        cursor.execute("""
            INSERT OR IGNORE INTO Dim_Artists (artist_name, primary_genre, spotify_popularity) 
            VALUES (?, ?, ?)""", (channel_name, genre, popularity))
        
        # Inject video dimensions linked back to artist references
        cursor.execute("""
            INSERT INTO Dim_Videos (artist_name, video_title, release_date) 
            VALUES (?, ?, ?)""", (channel_name, row['title'], row['publish_time']))
        
        # Inject metric logs tied into your structural dimension platforms
        cursor.execute("""
            INSERT INTO Fact_Video_Metrics (video_title, platform_id, view_count, likes_count, comment_count) 
            VALUES (?, ?, ?, ?, ?)""", 
            (row['title'], youtube_id, int(row['views']), int(row['likes']), int(row['comment_count'])))

    # 6. Tableau Export Layer: Generate an integrated analytical CSV file for business intelligence views
    print("Generating CSV asset for Tableau visualization...")
    tableau_query = """
        SELECT 
            a.artist_name, a.primary_genre, a.spotify_popularity,
            v.video_title, v.release_date,
            p.platform_name, p.syndicate_type,
            f.view_count, f.likes_count, f.comment_count
        FROM Fact_Video_Metrics f
        JOIN Dim_Videos v ON f.video_title = v.video_title
        JOIN Dim_Artists a ON v.artist_name = a.artist_name
        JOIN Dim_Platforms p ON f.platform_id = p.platform_id;
    """
    pd.read_sql_query(tableau_query, conn).to_csv(os.path.join("data", "tableau_analytics.csv"), index=False)

    # Save tracking changes permanently and release lock
    conn.commit()
    conn.close()
    print(f"\nSuccess! Pipeline executed. Local database '{DB_PATH}' created and fully seeded with integrated metrics.")

if __name__ == "__main__":
    run_integrated_pipeline()
