# README.md

## Python Flask App

A Flask application designed to be deployed on Cpanel, providing a template for building web applications.

# To run the project locally

## Local Development Setup

1. **Clone the repository:**

2. **Set up Python Virtual Environment and install dependencies:**
- Needs to be done at a CLI propmt with admin prviliges
   ```
   npm run setup
   ```

5. **Run the Development Server:**
   ```
   npm run dev
   ```
   The application will be available at `http://localhost:5000`

## Deploy to CPanel

1. Install a python app in the root folder rocksmith-plus, and set the URL to [domain-name]rocksmith-plus

2. Edit the passenger_wsgi.py file that will be automatically placed in the rocksmith-plus folder
```
import os
import sys

# Add application directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import Flask app
from src.app import app as application
```

3. Edit the .htaccess that will be placed in the public_html/rocksmith-plus folder
- Add the following two lines
```
RewriteEngine On 
RewriteRule ^http://%{HTTP_HOST}%{REQUEST_URI} [END,NE]
```

4. - Log in via ssh and execute ```source /home/michaelb/virtualenv/rocksmith-plus/3.9/bin/activate && cd /home/michaelb/rocksmith-plus```
   - Execute ```pip install -r requirements.txt```

4. Copy the src/static folder to the public_html/rocksmith-plus folder

5. Copy the src/api, src/template, src/utility folders, and the src/app.py file to the rocksmith-plus/src on the host

6. Copy the requirements.txt folder to the rocksmith-plus folder (root project directory)

7, Add the envioronment variables in the CPANEL python app

8. Restart the python app

### Notes

- the python logs can be dound in rocksmith-plus/stederr.log 

## Available Local Scripts

- `npm run setup` - Initial setup after cloning or installing new packages
- `npm run dev` - Run the web app locally on port 5000
- `npm clean` - Clean up the virtual environmentg if needed

## Requirements

- Python 3.8 or higher
- Node.js
- npm or yarn

## License

This project is licensed under the MIT License.

## Project Structure

```
Vercel-Rocksmith+
├── src/
│   ├── app.py            # Main Flask application
│   ├── templates/        # HTML templates
│   │   └── index.html    # Main page template
│   └── static/
│       └── css/
│           └── style.css # CSS styles
├── requirements.txt      # Python dependencies
├── package.json         # Node.js/Vercel configuration
├── vercel.json          # Vercel deployment settings
└── README.md           
```

## Usage

- Access the application in your browser at `http://localhost:5000` when running locally.
- Follow the Cpanel deployment instructions to access your application online.

## License

This project is licensed under the MIT License.

## Database Indexation

```
-- Index songs table
ALTER TABLE songs ADD INDEX idx_artist (artist);
ALTER TABLE songs ADD INDEX idx_title (title);
ALTER TABLE songs ADD INDEX idx_album (album);

-- Index lookup tables with unique constraints
ALTER TABLE genres ADD UNIQUE INDEX idx_genre_name (genre_name);
ALTER TABLE arrangements ADD UNIQUE INDEX idx_arrangement_name (arrangement_name);
ALTER TABLE regions ADD UNIQUE INDEX idx_region_code (region_code);

-- Index junction tables for faster lookups and joins
ALTER TABLE song_genres ADD INDEX idx_genre_id (genre_id);
ALTER TABLE song_genres ADD INDEX idx_song_genre (song_id, genre_id);

ALTER TABLE song_arrangements ADD INDEX idx_arrangement_id (arrangement_id);
ALTER TABLE song_arrangements ADD INDEX idx_song_arrangement (song_id, arrangement_id);

ALTER TABLE song_regions ADD INDEX idx_region_id (region_id);
ALTER TABLE song_regions ADD INDEX idx_song_region (song_id, region_id);
```