#Python Script for recommendations - 1. Popularity-Based 2. Content Based 3.Hybrid 


#Import necessary libraries
import pandas as pd
import numpy as np
from IPython.display import display
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

#Popularity Based Recommendations 
def popularity_based_recommendation_system(df, genres_list, top_n=5):
    recommendations = {}
    
    for genre in genres_list:
        genre_df = df[df['Genres'].apply(lambda x: genre in x)]
        
        if genre_df.empty:
            print(f"No data available for genre: {genre}")
            continue
        
        # Top tracks with artist and album details
        top_tracks = genre_df[['Track Name', 'Track ID', 'Artist Name', 'Album Name', 'Track Image', 'Track Popularity']].drop_duplicates().sort_values(by='Track Popularity', ascending=False).head(top_n)
        
        # Top artists
        top_artists = genre_df[['Artist Name', 'Artist ID', 'Followers', 'Artist Image']].drop_duplicates().sort_values(by='Followers', ascending=False).head(top_n)
        
        recommendations[genre] = {
            'top_tracks': top_tracks,
            'top_artists': top_artists
        }
    
    return recommendations


#Content Based Recommendation
def kpop_content_based_recommendation_system(df, genres_list, user_interactions, preferred_genres=None, top_n=10, weights=None):
    """
    Creates a content-based recommendation system for K-pop music based on genre similarity.

    Parameters:
    - df (DataFrame): The dataset containing K-pop songs.
    - genres_list (list): List of genres to be used for encoding.
    - user_interactions (list): List of tracks the user has interacted with.
    - preferred_genres (list): List of genres the user prefers (optional).
    - top_n (int): Number of recommendations to return (default is 10).
    - weights (dict): Weights for each genre in the similarity calculation (optional).

    Returns:
    - recommendations_df (DataFrame): DataFrame of recommended tracks.
    """
    # Step 1: Binary Encoding of Genres
    for genre in genres_list:
        df[genre] = df['Genres'].apply(lambda x: 1 if genre in x else 0)
    
    # Step 2: Genre Pivot Table and Optional Weighted Cosine Similarity
    genre_pivot = df.pivot_table(index='Track Name', columns=genres_list, aggfunc='sum', fill_value=0)
    
    if weights:
        for genre, weight in weights.items():
            if genre in genre_pivot.columns:
                genre_pivot[genre] = genre_pivot[genre] * weight
    
    similarity_matrix = cosine_similarity(genre_pivot)
    similarity_df = pd.DataFrame(similarity_matrix, index=genre_pivot.index, columns=genre_pivot.index)
    
    # Step 3: Generate Content-Based Recommendations
    recommendations = []
    valid_tracks = [track for track in user_interactions if track in similarity_df.index]
    
    for track in valid_tracks:
        similar_tracks = similarity_df[track].sort_values(ascending=False).head(top_n + 1)  # +1 to skip the track itself
        recommendations.extend(similar_tracks.index[1:])  # Exclude the track itself
    
    # Step 4: Filter Recommendations by User's Preferred Genres
    if preferred_genres:
        # Ensure 'k-pop' is included only if specified in preferred_genres
        if 'k-pop' not in preferred_genres:
            preferred_genres = [genre for genre in preferred_genres if genre != 'k-pop']
        
        recommendations = [
            track for track in recommendations 
            if any(genre in df.loc[df['Track Name'] == track, 'Genres'].values[0] for genre in preferred_genres)
        ]
    
    recommendations_df = df[df['Track Name'].isin(list(set(recommendations))[:top_n])]
    return recommendations_df


# Hybrid Recommendation System
def hybrid_recommendation_system(df, genres_list, user_interactions=None, preferred_genres=None, top_n=10, weights=None, pop_weight=0.5, content_weight=0.5):
    """
    Hybrid recommendation system combining popularity-based and content-based recommendations.

    Parameters:
    - df (DataFrame): The dataset containing K-pop songs.
    - genres_list (list): List of genres to be used for encoding.
    - user_interactions (list): List of tracks the user has interacted with (optional).
    - preferred_genres (list): List of genres the user prefers (optional).
    - top_n (int): Number of recommendations to return (default is 10).
    - weights (dict): Weights for each genre in the similarity calculation (optional).
    - pop_weight (float): Weight for the popularity-based recommendation.
    - content_weight (float): Weight for the content-based recommendation.

    Returns:
    - combined_recs (dict): Dictionary of recommended tracks by genre with detailed info.
    """
    combined_recs = {}
    
    # Get popularity-based recommendations
    if preferred_genres:
        pop_recs = popularity_based_recommendation_system(df, preferred_genres, top_n)
    else:
        pop_recs = popularity_based_recommendation_system(df, genres_list, top_n)
    
    # Print available genres in pop_recs
    print(f"Available genres in popularity recommendations: {pop_recs.keys()}")

    # Get content-based recommendations if user interactions are provided
    if user_interactions:
        content_recs = kpop_content_based_recommendation_system(df, genres_list, user_interactions, preferred_genres, top_n, weights)
    else:
        content_recs = []

    for genre in genres_list:
        if genre in pop_recs:
            pop_tracks_df = pop_recs[genre]['top_tracks'].head(top_n)
        else:
            print(f"Warning: Genre '{genre}' not found in popularity recommendations.")
            pop_tracks_df = pd.DataFrame(columns=df.columns)
        
        if user_interactions:
            content_tracks_df = df[df['Track Name'].isin(content_recs)]
        else:
            content_tracks_df = pd.DataFrame()
        
        combined_tracks_df = pd.concat([pop_tracks_df, content_tracks_df]).drop_duplicates().head(top_n)
        combined_recs[genre] = combined_tracks_df
    
    return combined_recs
