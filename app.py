import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "416d99e862d54b1397ae6e8907fe36ef"
CLIENT_SECRET = "ffcb9462b5354fe0b799499139b4160d"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Load the data
music = pickle.load(open('musicrec.pkl','rb'))
similarity = pickle.load(open('similarities.pkl','rb'))

# Extract the artist name from the tags 
# (assuming the first 2 words are the artist's name)
def get_artist_from_tags(tags):
    return ' '.join(tags.split()[:2]) # Extract the first 2 words as artist's name


### To fetch the preview URL
def get_song_details(song_name, artist_name):
    ### This creates a search query string for Spotify's API by combining the 
    ## song's name and the artist's name.
    search_query = f"track:{song_name} artist:{artist_name}"
    ### type="track": This specifies that the search is specifically for a track
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        ### This gets the first track from the list of search results. 
        # This assumes that the first result is the most relevant match.
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        preview_url = track.get("preview_url")  # Get the song preview URL
        return album_cover_url, preview_url
    else:
        # Default image and None if no preview URL
        return "https://i.postimg.cc/0QNxYz4V/social.png", None  



### To fetch the album cover URL:
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        ### This gets the first track from the list of search results. 
        # This assumes that the first result is the most relevant match.
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        print(album_cover_url)
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"



### To get artist name
def get_correct_artist_name(song_title):
    search_query = f"track:{song_title}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        # Extract artist names from the track
        spotify_artists = [artist['name'] for artist in track['artists']]
        return spotify_artists
    else:
        return None



#### recommend function
def recommend(song):
    index = music[music['title'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    recommended_music_previews = []

    for i in distances[1:6]:
        # Extract artist from tags
        tags = music.iloc[i[0]]['tags']
        artist_from_tags = get_artist_from_tags(tags)

        # Get the correct artist name from Spotify
        correct_artists = get_correct_artist_name(music.iloc[i[0]]['title'])

        # Fetch the album cover URL, song name, and preview URL
        album_cover_url, preview_url = get_song_details(music.iloc[i[0]]['title'], correct_artists)
        recommended_music_posters.append(album_cover_url)
        recommended_music_names.append(music.iloc[i[0]]['title'])
        recommended_music_previews.append(preview_url)

    return recommended_music_names, recommended_music_posters, recommended_music_previews








st.header('Music Recommendation System')






print(music.iloc[[0]]['title'])


music_list = music['title'].values
selected_song = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

import base64

# Function to convert image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Use the function to get the base64 string of your image
img_path = "C:/Users/HP/Documents/Documents/MCA/IBM_Training/PythonPrograms/Project/bg.png"
img_base64 = get_base64_of_bin_file(img_path)

# Define the background image using Base64
page_bg_img = f'''
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img_base64}");
background-size: cover;
background-position: center;
}}
</style>
'''

# Inject the CSS into Streamlit app
st.markdown(page_bg_img, unsafe_allow_html=True)

### To set header Dark background
# Inject custom CSS
st.markdown("""
    <style>
    /* General styling for all header elements */
    header {
        background-color: #1a1a1a !important;  /* Dark background color */
        color: white !important;               /* White text */
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Style the main app's background container */
    [data-testid="stAppViewContainer"] {
        background-color: #2c2c2c !important;  /* Dark background for the app */
    }

    /* Style Streamlit's main title element */
    .css-10trblm {
        color: white !important;               /* Ensure header text is white */
    }

    /* Style any other text within the header */
    .st-bw {
        color: white !important;
    }

    </style>
    """, unsafe_allow_html=True)




if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters, recommended_music_previews = recommend(selected_song)
    
    # Display the recommendations in columns
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Evenly spaced columns
    
    cols = [col1, col2, col3, col4, col5]
    
    for i, col in enumerate(cols):
        with col:
            st.text(recommended_music_names[i])
            st.image(recommended_music_posters[i])
            
            # If preview URL exists, add a play button
            if recommended_music_previews[i]:
                st.audio(recommended_music_previews[i], format='audio/mp3')  # Add the audio player below the image
            else:
                st.text("Preview not available")


