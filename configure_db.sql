-- Create the main songs table
CREATE TABLE songs (
    id INT PRIMARY KEY,
    artist VARCHAR(255),
    title VARCHAR(255),
    available BOOLEAN,
    album VARCHAR(255),
    album_cover VARCHAR(512),
    duration TIME,
    dlc VARCHAR(255),
    regions_available_count INT,
    regions_unavailable_count INT
);

-- Create genres table
CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE
);

-- Create song_genres junction table
CREATE TABLE song_genres (
    song_id INT,
    genre_id INT,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    PRIMARY KEY (song_id, genre_id)
);

-- Create arrangements table
CREATE TABLE arrangements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arrangement_name VARCHAR(50)
);

-- Create song_arrangements junction table
CREATE TABLE song_arrangements (
    song_id INT,
    arrangement_id INT,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (arrangement_id) REFERENCES arrangements(id),
    PRIMARY KEY (song_id, arrangement_id)
);

-- Create regions table
CREATE TABLE regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_code VARCHAR(2) UNIQUE
);

-- Create song_regions junction table
CREATE TABLE song_regions (
    song_id INT,
    region_id INT,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (region_id) REFERENCES regions(id),
    PRIMARY KEY (song_id, region_id)
);

-- Insert sample data for genres
INSERT INTO genres (genre_name) VALUES 
('rock'),
('pop'),
('metal'),
('blues'),
('country'),
('folk');

-- Insert sample data for arrangements
INSERT INTO arrangements (arrangement_name) VALUES 
('ai_bass'),
('ai_chord'),
('bass'),
('lead'),
('rhythm');

-- Insert sample data for regions
INSERT INTO regions (region_code) VALUES 
('AD'), ('AE'), ('AL'), ('AM'), ('AT'), ('AU'), ('AZ'), ('BA'), ('BD'), ('BE'),
('BG'), ('BN'), ('BO'), ('BR'), ('BS'), ('BT'), ('CA'), ('CH'), ('CL'), ('CO');
-- ... (continue for all region codes)

-- Example of inserting a song (you would need to do this for each song)
INSERT INTO songs VALUES (
    12864,
    'The Walters',
    'Black Moon',
    true,
    'Try Again',
    'https://i.scdn.co/image/ab67616d00001e02ce233c1541dbcc3fa5f1e0fb',
    '03:21',
    'rock',
    '',
    100,
    0
);

-- Example of linking song to genres
INSERT INTO song_genres (song_id, genre_id)
SELECT 12864, id FROM genres 
WHERE genre_name IN ('rock');

-- Example of linking song to arrangements
INSERT INTO song_arrangements (song_id, arrangement_id)
SELECT 12864, id FROM arrangements 
WHERE arrangement_name IN ('ai_bass', 'ai_chord', 'bass', 'lead');

-- Example of linking song to regions
INSERT INTO song_regions (song_id, region_id)
SELECT 12864, id FROM regions 
WHERE region_code IN ('AD', 'AE', 'AL', 'AM', 'AT', 'AU', 'AZ', 'BA', 'BD', 'BE');
-- ... (continue for all regions)