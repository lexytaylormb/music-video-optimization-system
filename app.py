import os
import sqlite3
import pandas as pd

# Define paths within your VS Code project workspace
DB_PATH = "video_syndicate.db"
CSV_PATH = os.path.join("data", "USvideos.csv")
SCHEMA_PATH = "schema.sql"

def run_data_pipeline():
    # 1. Verification Check: Ensure your raw Kaggle data is in position
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find raw file at {CSV_PATH}.")
        print("Please move your downloaded USvideos.csv file into the 'data' directory.")
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
    print("Extracting records from raw CSV file...")
    # Read core columns to save processing memory
    use_cols = ['title', 'channel_title', 'publish_time', 'views', 'likes', 'comment_count']
    df = pd.read_csv(CSV_PATH, usecols=use_cols)

    # 4. Transformation Phase: Strip out corrupted or missing rows
    print("Scrubbing anomalies and formatting data elements...")
    df = df.dropna(subset=['title', 'channel_title'])
    df = df[(df['views'] >= 0) & (df['likes'] >= 0)] # Remove numeric parsing glitches
    
    # Isolate a clean pool of rows to keep the demonstration lean and fast
    clean_records = df.head(2500)

    # 5. Load Phase: Safely transfer cleaned elements into structural database tables
    print("Loading records into the normalized database layout...")
    
    # Fetch platform IDs for our relational link keys
    cursor.execute("SELECT platform_id FROM Dim_Platforms WHERE platform_name = 'YouTube'")
    youtube_id = cursor.fetchone()[0]

    for _, row in clean_records.iterrows():
        # Inject artist dimensions into lookup maps securely
        cursor.execute("""
            INSERT OR IGNORE INTO Dim_Artists (artist_name) 
            VALUES (?)""", (row['channel_title'],))
        
        # Inject video dimensions linked back to artist references
        cursor.execute("""
            INSERT INTO Dim_Videos (artist_name, video_title, release_date) 
            VALUES (?, ?, ?)""", (row['channel_title'], row['title'], row['publish_time']))
        
        # Inject metric logs tied into your structural dimension platforms
        cursor.execute("""
            INSERT INTO Fact_Video_Metrics (video_title, platform_id, view_count, likes_count, comment_count) 
            VALUES (?, ?, ?, ?, ?)""", 
            (row['title'], youtube_id, int(row['views']), int(row['likes']), int(row['comment_count'])))

    # Save tracking changes permanently and release lock
    conn.commit()
    conn.close()
    print(f"\nSuccess! Pipeline executed. Local database '{DB_PATH}' created and fully seeded.")

if __name__ == "__main__":
    run_data_pipeline()