from dotenv import load_dotenv
import os
import pymysql
import csv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database configuration - handle escaped password
config = {
    'host': os.getenv('DATABASE_URL', 'localhost'),
    'user': os.getenv('DATABASE_USERNAME'),
    'password': os.getenv('DATABASE_PASSWORD').replace('\\$', '$') if os.getenv('DATABASE_PASSWORD') else None,
    'database': os.getenv('DATABASE_NAME'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'charset': 'utf8mb4'
}

def connect_to_database():
    try:
        config_final = config.copy()
        if config['host'] == 'localhost' and os.name != 'nt':  # Not Windows
            config_final['unix_socket'] = '/var/lib/mysql/mysql.sock'
        elif config['host'] == 'localhost' and os.name == 'nt':  # Windows
            config_final['port'] = 3306
            
        connection = pymysql.connect(**config_final)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print(f"Connected to database: {record[0]}")
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def disable_indexes_and_constraints(connection):
    """Disable indexes and constraints for faster insertion"""
    cursor = connection.cursor()
    
    print("🚀 Optimizing database for bulk insert...")
    
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Disable unique checks
    cursor.execute("SET UNIQUE_CHECKS = 0")
    
    # Disable autocommit for batch processing
    cursor.execute("SET AUTOCOMMIT = 0")
    
    # Increase bulk insert buffer
    cursor.execute("SET bulk_insert_buffer_size = 256000000")  # 256MB
    
    # Disable binary logging (if you have permissions)
    try:
        cursor.execute("SET SQL_LOG_BIN = 0")
    except:
        pass  # May not have permission, that's okay
    
    connection.commit()
    print("✅ Database optimized for bulk operations")

def enable_indexes_and_constraints(connection):
    """Re-enable indexes and constraints after insertion"""
    cursor = connection.cursor()
    
    print("🔧 Re-enabling database constraints...")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Re-enable unique checks
    cursor.execute("SET UNIQUE_CHECKS = 1")
    
    # Re-enable autocommit
    cursor.execute("SET AUTOCOMMIT = 1")
    
    # Reset bulk insert buffer
    cursor.execute("SET bulk_insert_buffer_size = 8192000")  # Default 8MB
    
    # Re-enable binary logging
    try:
        cursor.execute("SET SQL_LOG_BIN = 1")
    except:
        pass
    
    connection.commit()
    print("✅ Database constraints re-enabled")

def fast_bulk_insert_songs(connection, csv_file):
    """Fast bulk insert using optimized batch processing"""
    cursor = connection.cursor()
    
    # Prepare batch lists
    song_batch = []
    genre_batch = []
    arrangement_batch = []
    region_batch = []
    
    song_genre_batch = []
    song_arrangement_batch = []
    song_region_batch = []
    
    # Track existing lookup values to avoid duplicates
    genres_map = {}
    arrangements_map = {}
    regions_map = {}
    
    batch_size = 1000
    total_processed = 0
    
    print(f"📖 Reading CSV: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                song_id = int(row['ID'])
                
                # Prepare song data (matching actual database structure)
                song_data = (
                    song_id,
                    row['Artist'][:255] if row['Artist'] else '',
                    row['Title'][:255] if row['Title'] else '',
                    row['Available'].lower() == 'true',
                    row['Album'][:255] if row['Album'] else '',
                    row['Album Cover'][:512] if row['Album Cover'] else '',
                    row['Duration'] if row['Duration'] else None,
                    row['DLC'][:255] if row['DLC'] else '',
                    int(row['Regions Available Count']) if row['Regions Available Count'].strip() else 0,
                    int(row['Regions Unavailable Count']) if row['Regions Unavailable Count'].strip() else 0
                )
                song_batch.append(song_data)
                
                # Process genres
                genres = [g.strip() for g in row['Genres'].split('|') if g.strip()]
                for genre in genres:
                    if genre not in genres_map:
                        genres_map[genre] = len(genres_map) + 1
                        genre_batch.append((genres_map[genre], genre))
                    song_genre_batch.append((song_id, genres_map[genre]))
                
                # Process arrangements
                arrangements = [a.strip() for a in row['Arrangements'].split('|') if a.strip()]
                for arrangement in arrangements:
                    if arrangement not in arrangements_map:
                        arrangements_map[arrangement] = len(arrangements_map) + 1
                        arrangement_batch.append((arrangements_map[arrangement], arrangement))
                    song_arrangement_batch.append((song_id, arrangements_map[arrangement]))
                
                # Process regions
                regions = [r.strip() for r in row['Available Regions'].split('|') if r.strip()]
                for region in regions:
                    if region not in regions_map:
                        regions_map[region] = len(regions_map) + 1
                        region_batch.append((regions_map[region], region))
                    song_region_batch.append((song_id, regions_map[region]))
                
                total_processed += 1
                
                # Execute batch when it reaches batch_size
                if len(song_batch) >= batch_size:
                    execute_batch_inserts(cursor, song_batch, genre_batch, arrangement_batch, 
                                        region_batch, song_genre_batch, song_arrangement_batch, 
                                        song_region_batch)
                    
                    # Clear batches
                    song_batch = []
                    genre_batch = []
                    arrangement_batch = []
                    region_batch = []
                    song_genre_batch = []
                    song_arrangement_batch = []
                    song_region_batch = []
                    
                    print(f"✅ Processed {total_processed} songs...")
                    connection.commit()
                
            except Exception as e:
                print(f"❌ Error processing song {row.get('Title', 'Unknown')}: {e}")
                continue
        
        # Execute remaining batch
        if song_batch:
            execute_batch_inserts(cursor, song_batch, genre_batch, arrangement_batch, 
                                region_batch, song_genre_batch, song_arrangement_batch, 
                                song_region_batch)
            connection.commit()
    
    print(f"🎉 Bulk insert completed! Total songs: {total_processed}")
    return total_processed

def execute_batch_inserts(cursor, song_batch, genre_batch, arrangement_batch, 
                         region_batch, song_genre_batch, song_arrangement_batch, 
                         song_region_batch):
    """Execute all batch inserts"""
    
    # Insert lookup tables first (matching actual table structure)
    if genre_batch:
        cursor.executemany("INSERT IGNORE INTO genres (id, genre_name) VALUES (%s, %s)", genre_batch)
    
    if arrangement_batch:
        cursor.executemany("INSERT IGNORE INTO arrangements (id, arrangement_name) VALUES (%s, %s)", arrangement_batch)
    
    if region_batch:
        cursor.executemany("INSERT IGNORE INTO regions (id, region_code) VALUES (%s, %s)", region_batch)
    
    # Insert songs
    if song_batch:
        song_sql = """
        INSERT IGNORE INTO songs (id, artist, title, available, album, album_cover, 
                                duration, dlc, regions_available_count, regions_unavailable_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(song_sql, song_batch)
    
    # Insert relationships
    if song_genre_batch:
        cursor.executemany("INSERT IGNORE INTO song_genres (song_id, genre_id) VALUES (%s, %s)", song_genre_batch)
    
    if song_arrangement_batch:
        cursor.executemany("INSERT IGNORE INTO song_arrangements (song_id, arrangement_id) VALUES (%s, %s)", song_arrangement_batch)
    
    if song_region_batch:
        cursor.executemany("INSERT IGNORE INTO song_regions (song_id, region_id) VALUES (%s, %s)", song_region_batch)

def main():
    print("=== FAST BULK DATABASE POPULATION ===")
    print("This script optimizes the database for fast bulk insertion.")
    print("⚠️ WARNING: This will disable constraints during population!")
    
    confirm = input("\nProceed with fast population? (type 'YES' to continue): ")
    if confirm != 'YES':
        print("Operation cancelled.")
        return
    
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database")
        return
    
    try:
        start_time = datetime.now()
        
        # Optimize database for bulk insert
        disable_indexes_and_constraints(connection)
        
        # Perform bulk insert
        csv_file = 'fullsongscrape_20250925-180052_deduplicated_20250925-201729.csv'
        total_songs = fast_bulk_insert_songs(connection, csv_file)
        
        # Re-enable constraints
        enable_indexes_and_constraints(connection)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 POPULATION COMPLETE!")
        print(f"Total songs inserted: {total_songs}")
        print(f"Time taken: {duration}")
        print(f"Speed: {total_songs / duration.total_seconds():.1f} songs/second")
        
    except Exception as e:
        print(f"❌ Error during population: {e}")
        # Always re-enable constraints even on error
        enable_indexes_and_constraints(connection)
        
    finally:
        if connection:
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()