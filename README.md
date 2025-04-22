# README.md

## Vercel Flask App

A Flask application designed to be deployed on Vercel, providing a template for building web applications.

# To run the project locally

## Local Development Setup

1. **Clone the repository:**

2. **Set up Python Virtual Environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Python Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install Node.js Dependencies:**
   ```powershell
   npm install
   ```

5. **Run the Development Server:**
   ```powershell
   npm run dev
   ```
   The application will be available at `http://localhost:5000`

## Vercel Deployment

1. **Install Vercel CLI (if not already installed):**
   ```powershell
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```powershell
   vercel login
   ```

3. **Deploy to Vercel:**
   ```powershell
   npm run deploy
   ```

## Available Scripts

- `npm run dev` - Run Flask development server
- `npm run flask` - Run Flask directly through Python
- `npm run deploy` - Deploy to Vercel production
- `npm start` - Run Vercel development environment

## Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- Vercel CLI

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
## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-vercel-app
   ```

2. Activate the virtual environment and install the required dependencies:
   ```
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```
   python src/app.py
   ```

4. Deploy to Vercel:
   - Ensure you have the Vercel CLI installed.
   - Run the following command to deploy:
   ```
   vercel
   ```

## Usage

- Access the application in your browser at `http://localhost:5000` when running locally.
- Follow the Vercel deployment instructions to access your application online.

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