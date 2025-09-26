from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import csv

# Load environment variables
load_dotenv()

# Database configuration
config = {
    'host': os.getenv('DATABASE_URL', 'localhost'),
    'user': os.getenv('DATABASE_USERNAME'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'database': os.getenv('DATABASE_NAME'),
    'port': int(os.getenv('DATABASE_PORT', 3306))
}

def connect_to_database():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            db_info = connection.server_info
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None
    
def insert_song_data(connection, song_data):
    try:
        cursor = connection.cursor()
        
        # Prepare the song insert with a single query
        insert_song = """
        INSERT INTO songs (id, artist, title, available, album, album_cover, duration, dlc, 
                         regions_available_count, regions_unavailable_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        song_values = (
            int(song_data['ID']),
            song_data['Artist'],
            song_data['Title'],
            song_data['Available'].lower() == 'true',
            song_data['Album'],
            song_data['Album Cover'],
            song_data['Duration'],
            song_data['DLC'],
            int(song_data['Regions Available Count']),
            int(song_data['Regions Unavailable Count'])
        )
        
        # Use parameterized queries for better performance
        genres = [(genre,) for genre in song_data['Genres'].split('|') if genre]
        arrangements = [(arr,) for arr in song_data['Arrangements'].split('|') if arr]
        regions = [(region,) for region in song_data['Available Regions'].split('|') if region]
        
        # Disable autocommit and constraints temporarily
        cursor.execute("SET autocommit=0")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # Insert song
        cursor.execute(insert_song, song_values)
        
        # Batch insert relationships
        if genres:
            cursor.executemany("INSERT IGNORE INTO genres (genre_name) VALUES (%s)", genres)
            cursor.execute("""
                INSERT INTO song_genres (song_id, genre_id)
                SELECT %s, id FROM genres WHERE genre_name IN ({})
            """.format(','.join(['%s'] * len(genres))), 
            [song_data['ID']] + [g[0] for g in genres])
            
        if arrangements:
            cursor.executemany("INSERT IGNORE INTO arrangements (arrangement_name) VALUES (%s)", arrangements)
            cursor.execute("""
                INSERT INTO song_arrangements (song_id, arrangement_id)
                SELECT %s, id FROM arrangements WHERE arrangement_name IN ({})
            """.format(','.join(['%s'] * len(arrangements))), 
            [song_data['ID']] + [a[0] for a in arrangements])
            
        if regions:
            cursor.executemany("INSERT IGNORE INTO regions (region_code) VALUES (%s)", regions)
            cursor.execute("""
                INSERT INTO song_regions (song_id, region_id)
                SELECT %s, id FROM regions WHERE region_code IN ({})
            """.format(','.join(['%s'] * len(regions))), 
            [song_data['ID']] + [r[0] for r in regions])
        
        # Re-enable constraints and commit
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        connection.commit()
        
    except Error as e:
        print(f"Error processing song {song_data['Title']}: {e}")
        connection.rollback()
    finally:
        cursor.execute("SET autocommit=1")
        cursor.close()
    
def main():
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database")
        return
        
    try:
        csv_file = 'fullsongscrape_20250925-180052_deduplicated_20250925-201729.csv'
        processed_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    insert_song_data(connection, row)
                    processed_count += 1
                    if processed_count % 100 == 0:
                        print(f"Processed {processed_count} songs")
                except Error as e:
                    print(f"Error processing song {row.get('Title', 'Unknown')}: {e}")
                    continue

        print(f"\nCompleted processing {processed_count} songs")

    finally:
        if connection.is_connected():
            connection.cursor().close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()