#Pyhton script to retrieve data from Spotify Web API 

#Import libraries 
import requests
import base64
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os

# Initalize the values 
CLIENT_ID = "client id" # Replace with your Spotify API client ID
CLIENT_SECRET = "client secre"  # Replace with your Spotify API client secret   

#Authenticate the secret 
def get_access_token(client_id, client_secret):
    # Encode client_id and client_secret for Base64
    credentials = f"{client_id}:{client_secret}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()
    
    # Token request URL and headers
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {credentials_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    # Make the request for the access token
    response = requests.post(token_url, data=data, headers=headers)
    
    # Print status code and response text for debugging
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        access_token = response.json()['access_token']
        print("Access token obtained successfully.")
        return access_token
    else:
        print("Access token not obtained.")
        exit()

#Function to fetch data by genre
def fetch_data_by_genre(genre, access_token, data_type):
    base_url = f'https://api.spotify.com/v1/search'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    all_data = []
    search_url = f'{base_url}?q=genre:"{genre}"&type={data_type}&limit=50'
    
    while search_url:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        
        search_results = response.json()
        
        # Process results based on type
        items = search_results.get(data_type + 's', {}).get('items', [])
        
        for item in items:
            if data_type == 'artist':
                images = item.get('images', [])
                artist_image_url = images[0].get('url') if images else None
                
                all_data.append({
                    'Artist Name': item['name'],
                    'Artist ID': item['id'],
                    'Popularity': item.get('popularity', None),
                    'Followers': item.get('followers', {}).get('total', None),
                    'Genres': ', '.join(item.get('genres', [])),
                    'Genre Queried': genre,  # Track the genre that was queried
                    'Artist Image': artist_image_url  # Get the first image URL or None
                })
            elif data_type == 'track':
                album_images = item['album'].get('images', [])
                track_image_url = album_images[0].get('url') if album_images else None
                
                all_data.append({
                    'Track Name': item['name'],
                    'Track ID': item['id'],
                    'Duration (ms)': item.get('duration_ms', None),
                    'Popularity': item.get('popularity', None),
                    'Track Number': item.get('track_number', None),
                    'URI': item.get('uri', None),
                    'Album Name': item['album']['name'],
                    'Album ID': item['album']['id'],
                    'Artists': ', '.join(artist['name'] for artist in item.get('artists', [])),
                    'Genre Queried': genre,  # Track the genre that was queried
                    'Track Image': track_image_url  # Get the first image URL from album or None
                })
        
        # Check if there's a next page (pagination) and get the next set of results
        search_url = search_results.get(data_type + 's', {}).get('next', None)
        print(f"Fetching next page of {data_type} for genre: {genre}") if search_url else None
    
    return all_data


#Save the data as csv
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Get access token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

# List of genres
GENRES = ['k-pop','k-pop boy group', 'k-pop girl group', '5th gen k-pop','classic k-pop','korean r&b',
          'k-rap', 'atl hip hop', 'korean ost', 'korean pop', 'korean talent show', 'korean instrumental', 
          'korean trap', 'korean electronic', 'korean underground rap', 'classic korean pop', 
          'k-indie', 'korean bl ost', 'korean punk', 'trot', 'korean indie rock', 'k-pop ballad', 
          'korean hyperpop', 'korean metal', 'korean electropop', 'korean indie folk', 'korean soundtrack', 
          'korean superband', 'korean jazz', 'korean hardcore', 'korean musicals', 'korean shoegaze', 'korean experimental']

# Initialize lists to hold all artist and track data across genres
all_artists_data = []
all_tracks_data = []


# Fetch and accumulate data for each genre
for genre in GENRES:
    print(f"Fetching data for genre: {genre}")
    
    # Fetch data
    artists_data = fetch_data_by_genre(genre, access_token, 'artist')
    tracks_data = fetch_data_by_genre(genre, access_token, 'track')
    
    # Append to the master lists
    all_artists_data.extend(artists_data)
    all_tracks_data.extend(tracks_data)

# Save merged data to CSV files
save_to_csv(all_artists_data, 'all_artists_data.csv')
save_to_csv(all_tracks_data, 'all_tracks_data.csv')