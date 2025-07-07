import geopandas as gpd
import requests
import tempfile
import os
from difflib import get_close_matches

# This set is used to filter and standardize country names from the map data.
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

def unify_country_name(raw_name):
    """Finds the closest match for a country name from the valid list."""
    raw_lower = raw_name.lower()
    matches = get_close_matches(raw_lower, VALID_COUNTRIES, n=1, cutoff=0.75)
    return matches[0] if matches else ''

def create_geojson():
    """
    Downloads world map data, processes it, and saves it as a GeoJSON file.
    This file will contain only the necessary data for the web app.
    """
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "world.zip")
    
    print("Downloading world map data...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        print("Processing data...")
        # Read the shapefile
        world = gpd.read_file(f"zip://{temp_file}")
        
        # Standardize country names
        world['name'] = world['NAME'].apply(unify_country_name)
        
        # Filter out countries not in our valid list and keep only essential columns
        world = world[world['name'].isin(VALID_COUNTRIES)][['name', 'geometry']]
        
        # Ensure there are no rows with empty geometries
        world = world[~world.geometry.is_empty]
        
        # Save to GeoJSON
        output_filename = 'countries.geojson'
        world.to_file(output_filename, driver='GeoJSON')
        
        print(f"\nSuccess! Data saved to '{output_filename}'.")
        print("You can now upload 'index.html' and 'countries.geojson' to GitHub Pages.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

if __name__ == '__main__':
    create_geojson()