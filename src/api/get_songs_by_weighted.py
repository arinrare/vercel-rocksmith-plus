from flask import Blueprint, jsonify, request, session
from ..utility.database_connect import get_db_connection
import logging
from datetime import timedelta, datetime
import uuid

logger = logging.getLogger(__name__)
api_songs_weighted = Blueprint('songs_weighted_api', __name__)

def json_serializable(obj):
    """Convert datetime/timedelta objects to strings for JSON serialization"""
    if isinstance(obj, (datetime, timedelta)):
        return str(obj)
    return obj

@api_songs_weighted.route('/api/songs_weighted', methods=['POST'])
def get_songs():
    connection = get_db_connection()
    if connection is None:
        logger.error("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    if not data or 'genres' not in data:
        return jsonify({"error": "No genres provided"}), 400

    genres = data.get('genres', [])
    page = int(data.get('page', 1))
    per_page = 20  # Fixed page size
    
    if not genres:
        return jsonify({"error": "Empty genres list"}), 400

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if temp table exists and is accessible
        if 'search_table' in session:
            cursor.execute(f"""
                SELECT COUNT(*) as table_exists 
                FROM information_schema.tables 
                WHERE table_name = '{session['search_table']}'
            """)
            table_exists = cursor.fetchone()['table_exists'] > 0
        else:
            table_exists = False

        # Create temp table for new search or if previous table is gone
        if not table_exists:
            # Generate unique table name
            session['search_table'] = f"weighted_results_{uuid.uuid4().hex[:8]}"
            
            # Build CASE statement for genre weights
            genre_cases = []
            genre_values = []
            for genre_data in genres:
                genre = genre_data['genre']
                weight = float(genre_data['weight'])
                genre_cases.append(f"WHEN g.genre_name = %s THEN {weight}")
                genre_values.append(genre)

            # Create and populate temp table
            temp_table_query = f"""
                CREATE TEMPORARY TABLE {session['search_table']} (
                    id INT PRIMARY KEY,
                    title VARCHAR(255),
                    artist VARCHAR(255),
                    genres TEXT,
                    arrangements TEXT,
                    genre_score FLOAT
                )
                SELECT s.id, s.title, s.artist,
                    GROUP_CONCAT(DISTINCT g.genre_name) as genres,
                    GROUP_CONCAT(DISTINCT a.arrangement_name) as arrangements,
                    SUM(CASE 
                        {" ".join(genre_cases)}
                        ELSE 0 
                    END) as genre_score
                FROM songs s
                LEFT JOIN song_genres sg ON s.id = sg.song_id
                LEFT JOIN genres g ON sg.genre_id = g.id
                LEFT JOIN song_arrangements sa ON s.id = sa.song_id
                LEFT JOIN arrangements a ON sa.arrangement_id = a.id
                WHERE g.genre_name IN ({','.join(['%s'] * len(genre_values))})
                GROUP BY s.id
                HAVING genre_score > 0
                ORDER BY genre_score DESC
                LIMIT 500
            """
            cursor.execute(temp_table_query, genre_values + genre_values)
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM {session['search_table']}")
            session['total_results'] = cursor.fetchone()['total']

        # Calculate pagination
        offset = (page - 1) * per_page
        
        # Fetch page from temp table
        cursor.execute(f"""
            SELECT * FROM {session['search_table']}
            ORDER BY genre_score DESC
            LIMIT %s OFFSET %s
        """, [per_page, offset])
        
        songs = cursor.fetchall()
        
        # Convert to JSON-serializable format
        serializable_songs = [{k: json_serializable(v) for k, v in song.items()} 
                            for song in songs]
        
        total_pages = (session['total_results'] + per_page - 1) // per_page
        
        return jsonify({
            'songs': serializable_songs,
            'total': session['total_results'],
            'currentPage': page,
            'totalPages': total_pages,
            'hasMore': page < total_pages
        })

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()