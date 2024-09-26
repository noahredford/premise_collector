import requests
import json
import time
import pandas as pd

# Your Google Places API key
API_KEY = 'AIzaSyBPNbdtzdGDAuknFeoSl9jLAvgr3uN63vc'

# List of coordinates - place in parsed kml coordinates here. 
coordinates = [
]

# Search radius in meters
radius = 2500  # Reduce radius to ensure more granular queries

# Google Places API endpoint for Nearby Search
base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# List of place types to search for
place_types = [
    'restaurant',
    'city_hall',
    'school',
    'fast_food',
    'store',
    'shopping_mall',
    'supermarket',
    'cafe',
    'hospital'
]

# Function to make the API request
def get_places(latitude, longitude, radius, api_key, place_type=None, next_page_token=None):
    location = f"{latitude},{longitude}"
    params = {
        'location': location,
        'radius': radius,
        'key': api_key
    }
    if next_page_token:
        params['pagetoken'] = next_page_token
    if place_type:
        params['type'] = place_type  # Specify the place type

    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to fetch all results for a specific coordinate (with pagination limit)
def fetch_all_places(latitude, longitude, place_type=None):
    all_places = []
    next_page_token = None
    pagination_limit = 3  # Limit to 3 pages max to avoid looping too long
    current_page = 0

    while True:
        data = get_places(latitude, longitude, radius, API_KEY, place_type, next_page_token)
        
        if data:
            all_places.extend(data['results'])
            next_page_token = data.get('next_page_token', None)
            current_page += 1
            
            # Log progress
            print(f"Page {current_page} for coordinates {latitude}, {longitude}, places found: {len(data['results'])} for type {place_type}")

            # Break if no more pages or pagination limit is reached
            if not next_page_token or current_page >= pagination_limit:
                break
            
            # Google's API might need a slight delay between paginated requests
            time.sleep(2)
        else:
            break

    return all_places

# Aggregate all places data from all coordinates and place types
def fetch_places_for_all_coordinates_and_types(coordinate_list, place_types):
    all_places_data = []

    for latitude, longitude in coordinate_list:
        for place_type in place_types:
            print(f"Fetching places for coordinates: {latitude}, {longitude}, type: {place_type}")
            places = fetch_all_places(latitude, longitude, place_type)

            for place in places:
                place_info = {
                    'Place Name': place['name'],
                    'Latitude': place['geometry']['location']['lat'],
                    'Longitude': place['geometry']['location']['lng'],
                    'Address': place.get('vicinity', 'N/A'),
                    'Types': ', '.join(place['types']) if 'types' in place else 'N/A',
                    'Place Type': place_type  # Add the type of place being queried
                }
                all_places_data.append(place_info)

    return all_places_data

# Fetch places for all coordinates and place types
places_data = fetch_places_for_all_coordinates_and_types(coordinates, place_types)

# Convert the data to a pandas DataFrame
df = pd.DataFrame(places_data)

# Save the data to an Excel file
output_file_name = 'places_by_type_oatmeal_raisin.xlsx'  # File named after a cookie, you can change it
df.to_excel(output_file_name, index=False)

print(f"Data saved to {output_file_name}")
