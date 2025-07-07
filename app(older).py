# app.py
from flask import Flask, render_template, request, jsonify, session
import geopandas as gpd
import numpy as np
from shapely.ops import nearest_points
from math import degrees, atan2
import warnings
import requests
import tempfile
import os
import math
import sys
from difflib import get_close_matches

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Use environment variable for secret key

VALID_COUNTRIES = {
    'afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua and barbuda', 'argentina', 
    'armenia', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 
    'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 'bolivia', 
    'bosnia and herzegovina', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina faso', 
    'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde', 'central african republic', 
    'chad', 'chile', 'china', 'colombia', 'comoros', 'congo', 'costa rica', 'croatia', 
    'cuba', 'cyprus', 'czech republic', 'democratic republic of the congo', 'denmark', 
    'djibouti', 'dominica', 'dominican republic', 'ecuador', 'egypt', 'el salvador', 
    'equatorial guinea', 'eritrea', 'estonia', 'eswatini', 'ethiopia', 'fiji', 'finland', 
    'france', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'greece', 'grenada', 
    'guatemala', 'guinea', 'guinea-bissau', 'guyana', 'haiti', 'honduras', 'hungary', 
    'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy', 
    'ivory coast', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 
    'kuwait', 'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 
    'liechtenstein', 'lithuania', 'luxembourg', 'madagascar', 'malawi', 'malaysia', 
    'maldives', 'mali', 'malta', 'marshall islands', 'mauritania', 'mauritius', 'mexico', 
    'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique', 
    'myanmar', 'namibia', 'nauru', 'nepal', 'netherlands', 'new zealand', 'nicaragua', 
    'niger', 'nigeria', 'north korea', 'north macedonia', 'norway', 'oman', 'pakistan', 
    'palau', 'palestine', 'panama', 'papua new guinea', 'paraguay', 'peru', 'philippines', 
    'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda', 'saint kitts and nevis', 
    'saint lucia', 'saint vincent and the grenadines', 'samoa', 'san marino', 
    'sao tome and principe', 'saudi arabia', 'senegal', 'serbia', 'seychelles', 
    'sierra leone', 'singapore', 'slovakia', 'slovenia', 'solomon islands', 'somalia', 
    'south africa', 'south korea', 'south sudan', 'spain', 'sri lanka', 'sudan', 'suriname', 
    'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand', 
    'timor-leste', 'togo', 'tonga', 'trinidad and tobago', 'tunisia', 'turkey', 
    'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'united arab emirates', 
    'united kingdom', 'united states', 'uruguay', 'uzbekistan', 'vanuatu', 
    'vatican city', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe'
}

# Original helper functions remain unchanged
def unify_country_name(raw_name):
    raw_lower = raw_name.lower()
    matches = get_close_matches(raw_lower, VALID_COUNTRIES, n=1, cutoff=0.75)
    return matches[0] if matches else ''

def download_world_data():
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "world.zip")
    
    print("Downloading world map data...")
    response = requests.get(url)
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    world = gpd.read_file(f"zip://{temp_file}")
    os.remove(temp_file)
    os.rmdir(temp_dir)
    
    world['name_lower'] = world['NAME'].apply(unify_country_name)
    world = world[world.name_lower.isin(VALID_COUNTRIES)]
    return world

def calculate_direction(from_geom, to_geom):
    """Calculate direction between two country geometries using closest points"""
    p1, p2 = nearest_points(from_geom, to_geom)
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    bearing = degrees(atan2(dx, dy))
    bearing = (bearing + 360) % 360
    
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(bearing / 45) % 8
    return directions[index]

def calculate_border_distance(country1_geom, country2_geom):
    """Calculate shortest distance between country borders in km"""
    distance = country1_geom.distance(country2_geom)
    return round(distance * 100 / 10) * 10

# Functions for centroid-based calculations
def get_centroid_coords(geometry):
    """Calculate the centroid coordinates of a geometry. Returns (lat, lon)."""
    centroid = geometry.centroid
    return (centroid.y, centroid.x)

def calculate_bearing(pointA, pointB):
    """Calculate the bearing from pointA to pointB."""
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(diffLong)
    )

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def bearing_to_direction(bearing):
    """Convert bearing to cardinal direction."""
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    idx = int((bearing + 22.5) % 360 / 45)
    return directions[idx]

def get_neighbors(world_data, country_geometry):
    """Find neighboring countries by checking for shared borders."""
    neighbors = world_data[world_data.touches(country_geometry)]
    return neighbors

# Updated find_best_guess function with centroid fallback
def find_best_guess(world_data, current_country, target_distance, target_direction):
    """
    Find the best next guess based on distance and direction.
    Now includes fallback to centroid-based direction when no matches found with border-based approach.
    """
    current_geom = world_data[world_data.name_lower == current_country.lower()].geometry.iloc[0]
    
    # Handle neighboring countries case (<10km)
    if target_distance == 0:
        neighbors = get_neighbors(world_data, current_geom)
        if neighbors.empty:
            print(f"No neighboring countries found for '{current_country}'.")
            sys.exit(0)
        
        matching_neighbors = []
        country_centroid = get_centroid_coords(current_geom)
        
        for idx, neighbor in neighbors.iterrows():
            neighbor_centroid = get_centroid_coords(neighbor.geometry)
            bearing = calculate_bearing(country_centroid, neighbor_centroid)
            direction = bearing_to_direction(bearing)
            if direction == target_direction:
                matching_neighbors.append(neighbor['name_lower'].title())
        
        if matching_neighbors:
            print(f"\nSince the distance is <10km, country could be one of these:")
            for name in matching_neighbors:
                print(f"- {name}")
        else:
            print(f"\nNo bordering countries found to the {target_direction} of '{current_country}' within <10km.")
        sys.exit(0)
    
    # First attempt: Use border-based direction calculation
    best_country = None
    min_distance_diff = float('inf')
    
    for idx, row in world_data.iterrows():
        if row.name_lower == current_country.lower():
            continue
            
        direction = calculate_direction(current_geom, row.geometry)
        
        if direction == target_direction:
            distance = calculate_border_distance(current_geom, row.geometry)
            distance_diff = abs(distance - target_distance)
            if distance_diff < min_distance_diff:
                min_distance_diff = distance_diff
                best_country = row.name_lower
    
    # If no country found, fallback to centroid-based direction
    if best_country is None:
        current_centroid = get_centroid_coords(current_geom)
        
        for idx, row in world_data.iterrows():
            if row.name_lower == current_country.lower():
                continue
            
            target_centroid = get_centroid_coords(row.geometry)
            bearing = calculate_bearing(current_centroid, target_centroid)
            direction = bearing_to_direction(bearing)
            
            if direction == target_direction:
                distance = calculate_border_distance(current_geom, row.geometry)
                distance_diff = abs(distance - target_distance)
                if distance_diff < min_distance_diff:
                    min_distance_diff = distance_diff
                    best_country = row.name_lower

    return best_country.title() if best_country else None

def parse_distance(distance_str):
    """Parse distance input, handling '<10km' case"""
    if distance_str.strip().lower() == '<10km' or distance_str.strip().lower() == '<10':
        return 0
    try:
        return float(distance_str)
    except ValueError:
        raise ValueError("Invalid distance format. Please use a number or '<10km'")

def play_globle():
    try:
        world_data = download_world_data()
    except Exception as e:
        print(f"Error downloading world data: {e}")
        return
    
    # Get first guess without showing "Try this country"
    while True:
        current_guess = input("\nEnter your first guess country: ").lower()
        if current_guess in world_data.name_lower.tolist():
            current_guess = world_data.loc[world_data.name_lower == current_guess, 'name_lower'].iloc[0].title()
            break
        print("Country not found. Please check the spelling and try again.")
    
    # First iteration flag to control "Try this country" message
    is_first_iteration = True
    
    while True:
        # Only show "Try this country" after the first iteration
        if not is_first_iteration:
            print(f"\nTry this country: {current_guess}")
        is_first_iteration = False
            
        try:
            print("\nEnter distance and direction (e.g., '320km N' or '<10km SE')")
            feedback = input("Your input: ")
            
            parts = feedback.strip().split()
            if len(parts) != 2:
                print("Invalid input format. Please use format like '320km N' or '<10km SE'")
                continue
                
            distance_str = parts[0].lower().replace('km', '')
            distance = parse_distance(distance_str)
            
            direction = parts[1].upper()
            if direction not in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
                print("Invalid direction. Use N, NE, E, SE, S, SW, W, or NW")
                continue
            
            next_guess = find_best_guess(world_data, current_guess, distance, direction)
            
            if next_guess is None:
                print("Couldn't find a suitable next guess. Please check the inputs.")
                continue
                
            current_guess = next_guess
        
        except ValueError as e:
            print(f"Error: {e}")
            continue

@app.route('/')
def index():
    """Route for the main game page"""
    # Initialize or reset game state
    session['current_guess'] = None
    session['is_first_iteration'] = True
    return render_template('index.html')

@app.route('/initialize-game', methods=['POST'])
def initialize_game():
    """Initialize the game with the first guess"""
    try:
        data = request.get_json()
        current_guess = data.get('guess', '').lower()
        
        # Download world data (you might want to cache this)
        world_data = download_world_data()
        
        if current_guess in world_data.name_lower.tolist():
            current_guess = world_data.loc[world_data.name_lower == current_guess, 'name_lower'].iloc[0].title()
            session['current_guess'] = current_guess
            session['is_first_iteration'] = True
            return jsonify({
                'success': True,
                'message': f'Starting game with {current_guess}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Country not found. Please check the spelling and try again.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# Update the make_guess route in app.py to handle <10km case
@app.route('/make-guess', methods=['POST'])
def make_guess():
    """Process a guess and return the next country suggestion"""
    try:
        data = request.get_json()
        distance_str = data.get('distance', '').lower().replace('km', '')
        direction = data.get('direction', '').upper()
        
        # Validate inputs
        if direction not in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            return jsonify({
                'success': False,
                'message': 'Invalid direction. Use N, NE, E, SE, S, SW, W, or NW'
            })
        
        current_guess = session.get('current_guess')
        if not current_guess:
            return jsonify({
                'success': False,
                'message': 'No current guess found. Please start a new game.'
            })
            
        distance = parse_distance(distance_str)
        world_data = download_world_data()
        
        # Special handling for <10km case
        if distance == 0:
            current_geom = world_data[world_data.name_lower == current_guess.lower()].geometry.iloc[0]
            neighbors = get_neighbors(world_data, current_geom)
            
            if neighbors.empty:
                return jsonify({
                    'success': False,
                    'message': f"No neighboring countries found for '{current_guess}'."
                })
            
            matching_neighbors = []
            country_centroid = get_centroid_coords(current_geom)
            
            for idx, neighbor in neighbors.iterrows():
                neighbor_centroid = get_centroid_coords(neighbor.geometry)
                bearing = calculate_bearing(country_centroid, neighbor_centroid)
                direction_calc = bearing_to_direction(bearing)
                if direction_calc == direction:
                    matching_neighbors.append(neighbor['name_lower'].title())
            
            if matching_neighbors:
                return jsonify({
                    'success': True,
                    'neighboring_countries': matching_neighbors
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f"No bordering countries found to the {direction} of '{current_guess}' within <10km."
                })
        
        # Normal case (>10km)
        next_guess = find_best_guess(world_data, current_guess, distance, direction)
        
        if next_guess is None:
            return jsonify({
                'success': False,
                'message': 'Could not find a suitable next guess. Please check the inputs.'
            })
            
        session['current_guess'] = next_guess
        session['is_first_iteration'] = False
        
        return jsonify({
            'success': True,
            'next_guess': next_guess
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        })

if __name__ == '__main__':
    # Use port and host from environment variables, default to 5000 and '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)
