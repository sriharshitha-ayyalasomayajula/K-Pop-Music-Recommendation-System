#Python Script for data processing and analysis
#Can be ran individually.

#Import necessary libraires
import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Data Loading
def load_data(artists_file, tracks_file):
    artists_df = pd.read_csv(artists_file)
    tracks_df = pd.read_csv(tracks_file)
    return artists_df, tracks_df

# Data Cleaning and Preparation
def clean_and_prepare_data(artists_df, tracks_df, genres_list):
    # Fill NaN and explode genres
    artists_df['Genres'] = artists_df['Genres'].fillna('')
    artists_df['Genres'] = artists_df['Genres'].str.split(', ')
    artists_df = artists_df.explode('Genres')
    
    # Filter for specific genres
    artists_df = artists_df[artists_df['Genres'].isin(genres_list)]
    
    # Merge tracks and artists data
    tracks_df.rename(columns={'Artists': 'Artist Name'}, inplace=True)
    combined_df = pd.merge(tracks_df, artists_df, on='Artist Name', how='inner')
    
    # Rename columns for clarity
    combined_df.rename(columns={
        'Popularity_x': 'Track Popularity',
        'Popularity_y': 'Artist Popularity',
        'Genre Queried_x': 'Track GQ',
        'Genre Queried_y': 'Artist GQ'
    }, inplace=True)
    
    return combined_df

# Plotting function for Artist Comparison
def plot_artists_comparison(df, genre, top_n=10):
    genre_df = df[df['Genres'] == genre]
    
    # Top artists by followers
    top_artists_followers = genre_df.nlargest(top_n, 'Followers')
    fig_followers = px.bar(top_artists_followers, x='Artist Name', y='Followers', color='Followers')
    
    # Top artists by popularity
    top_artists_popularity = genre_df.nlargest(top_n, 'Artist Popularity')
    fig_popularity = px.bar(top_artists_popularity, x='Artist Name', y='Artist Popularity', color='Artist Popularity')
    
    # Create subplots for comparison
    fig = make_subplots(rows=1, cols=2)
    for trace in fig_followers.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in fig_popularity.data:
        fig.add_trace(trace, row=1, col=2)
    
    fig.update_layout(title=f'{genre} - Top Artists Comparison - Followers V/S Popularity')
    fig.show()
    

# Plot top artists by album popularity
def plot_top_artists_by_album_popularity(df):
    artist_popularity = df.groupby('Artist Name')['Track Popularity'].mean().reset_index(name='Average Track Popularity')
    most_popular_tracks = df.loc[df.groupby('Artist Name')['Track Popularity'].idxmax()][['Artist Name', 'Track Name', 'Album Name', 'Track Popularity']]
    artist_info = pd.merge(artist_popularity, most_popular_tracks, on='Artist Name')
    top_artists = artist_info.nlargest(10, 'Average Track Popularity')
    fig = px.bar(top_artists, x='Artist Name', y='Average Track Popularity', color='Artist Name',title='Top 10 Artists by Popular Albums')
    fig.show()
    
# Function to calculate number of tracks in an album
def calculate_tracks_per_album(df):
    return df.groupby('Album Name')['Track Name'].count().reset_index(name='Number of Tracks')

# Plot top albums by track popularity
def plot_top_albums_by_track_popularity(df):
    album_popularity = df.groupby('Album Name')['Track Popularity'].mean().reset_index(name='Average Track Popularity')
    top_albums = album_popularity.nlargest(10, 'Average Track Popularity')
    
    fig = px.bar(top_albums, x='Album Name', y='Average Track Popularity', color='Album Name',
                 title='Top 10 Albums by Popular Tracks')
    fig.show()

# Plot top artists by followers
def plot_top_artists_by_followers(df):
    followers_per_artist = df.groupby('Artist Name')['Followers'].mean().reset_index(name='Average Followers')
    top_artists_followers = followers_per_artist.nlargest(10, 'Average Followers')
    
    fig = px.bar(top_artists_followers, x='Artist Name', y='Average Followers', color='Artist Name',
                 title='Top 10 Artists by Followers')
    fig.show()
    
    
# Main function to execute the entire workflow
def main():
    # Define file paths
    artists_file = 'data/all_artists_data.csv'
    tracks_file = 'data/all_tracks_data.csv'
    
    # Load data
    artists_df, tracks_df = load_data(artists_file, tracks_file)
    
    # Define genres list
    genres_list = ['k-pop', 'k-pop boy group', 'k-pop girl group', '5th gen k-pop', 'classic k-pop',
                   'korean r&b', 'k-rap', 'korean ost', 'korean pop', 'classic korean pop', 'k-indie', 
                   'trot', 'k-pop ballad', 'korean soundtrack']
    
    # Clean and prepare data
    combined_df = clean_and_prepare_data(artists_df, tracks_df, genres_list)
    
    # Data visualization
    for genre in genres_list:
        plot_artists_comparison(combined_df, genre, top_n=10)
    
    # Plot top artists by album popularity
    plot_top_artists_by_album_popularity(combined_df)
     
    # Plot top albums by track popularity
    plot_top_albums_by_track_popularity(combined_df)
    
    # Plot top artists by followers
    plot_top_artists_by_followers(combined_df)
    

# Run the script
if __name__ == "__main__":
    main()


