#Python Script to build a streamlit app 

#Import necessary libraries 
import streamlit as st
import pandas as pd
from data_processing import load_data, clean_and_prepare_data
from recommendation_system import popularity_based_recommendation_system, kpop_content_based_recommendation_system, hybrid_recommendation_system

# Load Data
artists_file = 'data/all_artists_data.csv'
tracks_file = 'data/all_tracks_data.csv'
artists_df, tracks_df = load_data(artists_file, tracks_file)

# Define genres list
genres_list = ['k-pop', 'k-pop boy group', 'k-pop girl group', '5th gen k-pop', 'classic k-pop',
               'korean r&b', 'k-rap', 'korean ost', 'korean pop', 'classic korean pop', 'k-indie', 
               'trot', 'k-pop ballad', 'korean soundtrack']

# Clean and prepare data
combined_df = clean_and_prepare_data(artists_df, tracks_df, genres_list)

# Remove duplicates from the combined DataFrame
combined_df = combined_df.drop_duplicates()

# Optionally, reset index after dropping duplicates
combined_df = combined_df.reset_index(drop=True)

# Before displaying or recommending tracks, remove duplicates
combined_df_clean = combined_df.drop_duplicates(subset=['Track Name', 'Track ID', 'URI'], keep='first')

# Print column names to verify
#st.write("Columns in DataFrame:", combined_df_clean.columns)
#output_path = '/Users/sriharshithaayyalasomayajula/kpop_recommendation_app/data/combined_data.csv'
#combined_df_clean.to_csv(output_path, index=False)

# Main App Layout
st.title("K-POP Music Recommendation System")

# Step 1: Navigation
st.sidebar.title("Navigation")
nav_option = st.sidebar.radio("Go to", ["Home", "Get Recommendation"])

if nav_option == "Home":
    # Step 1: Genre Selection
    st.subheader("Select a Genre to Explore")
    genre = st.selectbox("Choose a genre", options=genres_list)

    # Step 2: Display Top Tracks and Artists
    if genre:
        st.write(f"Top 10 Artists and Tracks in {genre}")
        
        recommendations = popularity_based_recommendation_system(combined_df_clean, [genre], top_n=10)
        
        top_tracks = recommendations[genre]['top_tracks']
        top_artists = recommendations[genre]['top_artists']
        
        # Display top tracks with numbering
        st.write("### Top 10 Tracks")
        for i in range(0, len(top_tracks), 5):  # 5 items per row
            cols = st.columns(5)
            for j, (col, (_, row)) in enumerate(zip(cols, top_tracks.iloc[i:i+5].iterrows())):
                spotify_url = f"https://open.spotify.com/track/{row['Track ID']}"
                track_image_url = row.get('Track Image')  # Get track image URL
                col.image(track_image_url, use_column_width=True)  # Display track image
                col.write(f"**{i + j + 1}. {row['Track Name']}**")
                col.write(f"Artist: {row['Artist Name']}")
                col.write(f"Album: {row['Album Name']}")
                col.write(f"Popularity: {row['Track Popularity']}")
                col.write(f"[Listen on Spotify]({spotify_url})")
                
        
        # Display top artists with numbering and Spotify profile links
        st.write("### Top 10 Artists")
        for i in range(0, len(top_artists), 5):  # 5 items per row
            cols = st.columns(5)
            for j, (col, (_, row)) in enumerate(zip(cols, top_artists.iloc[i:i+5].iterrows())):
                spotify_url = f"https://open.spotify.com/artist/{row['Artist ID']}"
                artist_image_url = row.get('Artist Image')  # Get artist image URL
                col.image(artist_image_url, use_column_width=True)  # Display artist image
                col.write(f"**{i + j + 1}. {row['Artist Name']}**")
                col.write(f"Followers: {row['Followers']}")
                col.write(f"[Listen on Spotify]({spotify_url})")
    else:
        # Default to K-pop if no genre is selected
        st.write("Top 10 Artists and Tracks in K-pop")

elif nav_option == "Get Recommendation":
    st.header("Get Personalized Recommendations")
    
    # Step 3: Get User Input
    st.subheader("Enter the Track Name(s) (Optional)")
    track_options = combined_df_clean['Track Name'].unique()
    selected_tracks = st.multiselect("Select tracks you like", options=track_options)
    
    st.subheader("Choose your preferred genres (Optional)")
    preferred_genres = st.multiselect("Choose your preferred genres", options=genres_list)
    
    # Step 4: Generate Recommendations
    if st.button("Get Recommendations"):
        if not preferred_genres and not selected_tracks:
            st.write("Please select at least one genre or track to get recommendations.")
        else:
            # Call the hybrid recommendation system with optional user inputs
            hybrid_recs = hybrid_recommendation_system(
                combined_df_clean,
                genres_list,
                user_interactions=selected_tracks if selected_tracks else None,
                preferred_genres=preferred_genres if preferred_genres else None,
                top_n=10
            )
            
            if preferred_genres:
                if len(preferred_genres) == 1:
                    # Display recommendations only for the single selected genre
                    genre = preferred_genres[0]
                    if genre in hybrid_recs:
                        tracks_df = hybrid_recs[genre]
                        if isinstance(tracks_df, pd.DataFrame):
                            st.write(f"### Recommended Tracks for Genre: {genre}")
                            
                            # Display recommendations in rows of 5
                            for i in range(0, len(tracks_df), 5):
                                cols = st.columns(5)
                                for j, (col, track_row) in enumerate(zip(cols, tracks_df.iloc[i:i+5].iterrows())):
                                    index, row = track_row
                                    spotify_url = f"https://open.spotify.com/track/{row['Track ID']}"
                                    col.write(f"**{i + j + 1}. {row['Track Name']}**")
                                    col.write(f"Artist: {row['Artist Name']}")
                                    if 'Track Image' in row and pd.notna(row['Track Image']):
                                        col.image(row['Track Image'])
                                    col.write(f"[Listen on Spotify]({spotify_url})")
                        else:
                            st.write(f"Error: Expected DataFrame but got {type(tracks_df)}")
                    else:
                        st.write(f"No recommendations available for genre: {genre}")
                else:
                    # Display recommendations for all selected genres
                    for genre in preferred_genres:
                        if genre in hybrid_recs:
                            tracks_df = hybrid_recs[genre]
                            if isinstance(tracks_df, pd.DataFrame):
                                st.write(f"### Recommended Tracks for Genre: {genre}")
                                
                                # Display recommendations in rows of 5
                                for i in range(0, len(tracks_df), 5):
                                    cols = st.columns(5)
                                    for j, (col, track_row) in enumerate(zip(cols, tracks_df.iloc[i:i+5].iterrows())):
                                        index, row = track_row
                                        spotify_url = f"https://open.spotify.com/track/{row['Track ID']}"
                                        col.write(f"**{i + j + 1}. {row['Track Name']}**")
                                        col.write(f"Artist: {row['Artist Name']}")
                                        if 'Track Image' in row and pd.notna(row['Track Image']):
                                            col.image(row['Track Image'])
                                        col.write(f"[Listen on Spotify]({spotify_url})")
                            else:
                                st.write(f"Error: Expected DataFrame but got {type(tracks_df)}")
                        else:
                            st.write(f"No recommendations available for genre: {genre}")
            else:
                # Handle cases where only track selections are made
                if selected_tracks:
                    st.write("### Recommended Tracks Based on Your Selected Tracks")
                    
                    # Assuming you have a method to get recommendations based on selected tracks alone
                    track_based_recs = kpop_content_based_recommendation_system(
                                    combined_df_clean,
                                    genres_list,
                                    user_interactions=selected_tracks if selected_tracks else [],
                                    preferred_genres=preferred_genres if preferred_genres else None,
                                     top_n=10
                     )
            
                    
                    if isinstance(track_based_recs, pd.DataFrame):
                        if not track_based_recs.empty:
                            st.write("### Recommendations Based on Selected Tracks")
                            
                            # Display recommendations in rows of 5
                            for i in range(0, len(track_based_recs), 5):
                                cols = st.columns(5)
                                for j, (col, track_row) in enumerate(zip(cols, track_based_recs.iloc[i:i+5].iterrows())):
                                    index, row = track_row
                                    spotify_url = f"https://open.spotify.com/track/{row['Track ID']}"
                                    col.write(f"**{i + j + 1}. {row['Track Name']}**")
                                    col.write(f"Artist: {row['Artist Name']}")
                                    if 'Track Image' in row and pd.notna(row['Track Image']):
                                        col.image(row['Track Image'])
                                    col.write(f"[Listen on Spotify]({spotify_url})")
                        else:
                            st.write("No recommendations available based on the selected tracks.")
                    else:
                        st.write(f"Error: Expected DataFrame but got {type(track_based_recs)}")
