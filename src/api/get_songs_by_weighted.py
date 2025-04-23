from flask import Blueprint, jsonify, request
from ..utility.database_connect import get_db_connection
import logging
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

api_songs_weighted = Blueprint('songs_weighted_api', __name__)

def json_serializable(obj):
    if isinstance(obj, (datetime, timedelta)):
        return str(obj)
    return obj

@api_songs_weighted.route('/api/songs_weighted', methods=['POST'])
def get_songs():
    connection = get_db_connection()
    if connection is None:
        logger.error("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    # Get genre weights from request
    data = request.get_json()
    if not data or 'genres' not in data:
        return jsonify({"error": "No genres provided"}), 400

    genres = data['genres']
    if not genres:
        return jsonify({"error": "Empty genres list"}), 400

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Build dynamic query based on genre weights
        query = """
            SELECT s.*, 
                GROUP_CONCAT(DISTINCT g.genre_name) as genres,
                GROUP_CONCAT(DISTINCT a.arrangement_name) as arrangements,
                SUM(CASE 
                    {genre_cases}
                    ELSE 0 
                END) as genre_score
            FROM songs s
            LEFT JOIN song_genres sg ON s.id = sg.song_id
            LEFT JOIN genres g ON sg.genre_id = g.id
            LEFT JOIN song_arrangements sa ON s.id = sa.song_id
            LEFT JOIN arrangements a ON sa.arrangement_id = a.id
            WHERE g.genre_name IN ({genre_list})
            GROUP BY s.id
            HAVING genre_score > 0
            ORDER BY genre_score DESC
            LIMIT 20
        """

        # Build CASE statement for each genre weight
        genre_cases = []
        genre_values = []
        for genre_data in genres:
            genre = genre_data['genre']
            weight = float(genre_data['weight'])
            genre_cases.append(f"WHEN g.genre_name = %s THEN {weight}")
            genre_values.append(genre)

        # Format the query with the dynamic CASE statement
        formatted_query = query.format(
            genre_cases="\n".join(genre_cases),
            genre_list=','.join(['%s'] * len(genre_values))
        )

        # Execute with all genre values (used twice in query)
        cursor.execute(formatted_query, genre_values + genre_values)
        songs = cursor.fetchall()
        
        # Convert datetime/timedelta objects to strings
        serializable_songs = [{k: json_serializable(v) for k, v in song.items()} for song in songs]
        
        return jsonify(serializable_songs)
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()