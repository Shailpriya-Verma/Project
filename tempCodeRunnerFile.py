import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import base64

CLIENT_ID = "416d99e862d54b1397ae6e8907fe36ef"
CLIENT_SECRET = "ffcb9462b5354fe0b799499139b4160d"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get the album cover URL
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

# Function to get the track URI for playing (added)
def get_track_uri(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    print(search_query)
    results = sp.search(q=search_query, type="track")
    print(results)
    print(search_query)

    if results and results["tracks"]["items"]:
        track_uri = results["tracks"]["items"][0]["uri"]
        print(track_uri)
        return track_uri
    else:
        print("None")
        return None


# Extract the artist name from the tags (assuming the first 2 words are the artist's name)
def get_artist_from_tags(tags):
    return ' '.join(tags.split()[:2])  # Extract the first 2 words as artist's name





# Function to fetch the correct artist name for a song
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

# Main recommendation function with the added play button
def recommend(song):
    index = music[music['title'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    
    for i in distances[1:6]:
        # Extract artist from tags
        tags = music.iloc[i[0]]['tags']
        artist_from_tags = get_artist_from_tags(tags)

        # Get the correct artist name from Spotify
        correct_artists = get_correct_artist_name(music.iloc[i[0]]['title'])
        
        # Fetch the album cover URL and song name
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]]['title'], correct_artists[0] if correct_artists else artist_from_tags))
        recommended_music_names.append(music.iloc[i[0]]['title'])

        # Debug info
        # print(f"Dataset artist name: {artist_from_tags}")
        # print(f"Spotify artist names: {correct_artists}")

    return recommended_music_names, recommended_music_posters, correct_artists


# Streamlit UI
st.header('Music Recommendation System')

# Load the data
music = pickle.load(open('musicrec.pkl','rb'))
similarity = pickle.load(open('similarities.pkl','rb'))


import base64

# Function to convert image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
# Music selection dropdown
music_list = music['title'].values
selected_song = st.selectbox("Type or select a song from the dropdown", music_list)

# Background Image Logic (kept from your existing code)
img_path = "C:/Users/HP/Documents/Documents/MCA/IBM_Training/PythonPrograms/Project/bg.png"
img_base64 = get_base64_of_bin_file(img_path)
page_bg_img = f'''
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img_base64}");
background-size: cover;
background-position: center;
}}
</style>
'''
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

# Display Recommendations and Play Button
if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters, correct_artists = recommend(selected_song)
    
    # Display the recommendations in columns
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Evenly spaced columns

    cols = [col1, col2, col3, col4, col5]

    for i in range(5):
        with cols[i]:
            st.text(recommended_music_names[i])
            st.image(recommended_music_posters[i])
            
            # Add the play button
            if st.button(f"Play {i+1}", key=f"play_{i}"):  # Unique key for each button
                track_uri = get_track_uri(recommended_music_names[i], correct_artists[i][0] if correct_artists[i] else "")
                if track_uri:
                    st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_uri}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
                else:
                    st.error("Song not found on Spotify.")
