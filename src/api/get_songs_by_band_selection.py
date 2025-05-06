from flask import Blueprint, jsonify, request, session
from ..utility.database_connect import get_db_connection
import logging
from datetime import timedelta, datetime
import uuid
import json

logger = logging.getLogger(__name__)
api_songs_bands = Blueprint('songs_bands_api', __name__)

def json_serializable(obj):
    """Convert datetime/timedelta objects to strings for JSON serialization"""
    if isinstance(obj, (datetime, timedelta)):
        return str(obj)
    return obj

@api_songs_bands.route('/api/songs_bands', methods=['POST'])
def get_songs_by_bands():
    connection = get_db_connection()
    if connection is None:
        logger.error("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    if not data or 'genres' not in data:
        return jsonify({"error": "No band data provided"}), 400

    bands = data.get('genres', [])
    page = int(data.get('page', 1))
    per_page = 20  # Fixed page size

    total_requested = min(int(data.get('totalRequested', 500)), 500)

    if not bands:
        return jsonify({"error": "No bands provided"}), 400
    

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

        if not table_exists:
            session['search_table'] = f"band_results_{uuid.uuid4().hex[:8]}"
            
            # Process bands data in Python instead of JSON_TABLE
            genre_list = []
            for band in bands:
                if 'genres' in band:
                    genre_list.extend([g.lower() for g in band['genres'] if g])
            
            # Remove duplicates while preserving order
            unique_genres = list(dict.fromkeys(genre_list))
            
            # Create placeholders for IN clause
            genre_placeholders = ','.join(['%s'] * len(unique_genres))

            temp_table_query = f"""
                CREATE TEMPORARY TABLE {session['search_table']} (
                    id INT PRIMARY KEY,
                    title VARCHAR(255),
                    artist VARCHAR(255),
                    genres TEXT,
                    arrangements TEXT,
                    match_score FLOAT
                )
                SELECT 
                    s.id,
                    s.title,
                    s.artist,
                    GROUP_CONCAT(DISTINCT g.genre_name) as genres,
                    GROUP_CONCAT(DISTINCT 
                        CASE a.arrangement_name
                            WHEN 'ai_bass' THEN 'iconAIBass.png'
                            WHEN 'ai_chord' THEN 'iconAIChord.png'
                            WHEN 'bass' THEN 'iconBass.png'
                            WHEN 'lead' THEN 'iconLead.png'
                            WHEN 'rhythm' THEN 'iconRhythm.png'
                            WHEN 'keyboard' THEN 'iconKeyboard.png'
                            WHEN 'simple_keyboard' THEN 'iconSimpleKeyboard.png'
                            WHEN 'alt_lead' THEN 'iconALTLead.png'
                            WHEN 'alt_bass' THEN 'iconALTBass.png'
                            WHEN 'simple_guitar' THEN 'iconSimpleGuitar.png'
                            WHEN 'alt_rhythm' THEN 'iconALTRhythm.png'
                            ELSE NULL
                        END
                    ) as arrangements,
                    COUNT(DISTINCT CASE 
                        WHEN LOWER(g.genre_name) IN ({genre_placeholders})
                        THEN g.genre_name
                        ELSE NULL
                    END) as match_score
                FROM songs s
                LEFT JOIN song_genres sg ON s.id = sg.song_id
                LEFT JOIN genres g ON sg.genre_id = g.id
                LEFT JOIN song_arrangements sa ON s.id = sa.song_id
                LEFT JOIN arrangements a ON sa.arrangement_id = a.id
                GROUP BY s.id
                HAVING match_score > 0
                ORDER BY match_score DESC, s.title
                LIMIT %s
            """
            # Execute with flattened genre list
            cursor.execute(temp_table_query, unique_genres + [total_requested])
            
            # Get total count after creating table
            cursor.execute(f"SELECT COUNT(*) as total FROM {session['search_table']}")
            result = cursor.fetchone()
            session['total_results'] = result['total'] if result else 0

        # Calculate pagination
        offset = (page - 1) * per_page
        
        # Fetch page from temp table
        cursor.execute(f"""
            SELECT * FROM {session['search_table']}
            ORDER BY match_score DESC
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