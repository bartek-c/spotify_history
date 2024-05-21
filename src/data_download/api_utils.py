import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

BASE_URL = "https://api.spotify.com/v1/"

class HTTPError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"HTTP request failed with status code {status_code}")

def authorize_user(scope='user-library-read'):
    """
    Constructs the authorization URL for a user to 
    grant access to the application via the Spotify API.
    """
    credentials = load_app_credentials()
    
    params = {
        'client_id': credentials['CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': credentials['REDIRECT_URI'],
        'scope': scope
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
    print("Go to the following URL and authorize access:", auth_url)

    return auth_url

def load_app_credentials():
    if not load_dotenv():
        print("Error - could not get app credentials")
    
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("REDIRECT_URI")

    credentials = {
        'CLIENT_ID':CLIENT_ID,
        'CLIENT_SECRET':CLIENT_SECRET,
        'REDIRECT_URI':REDIRECT_URI
    }
    
    return credentials

class SpotifyAPI():
    def __init__(self, auth_code):
        self.auth_code=auth_code
        self.app_credentials=load_app_credentials()

    def get_access_token(self):
        """
        Exchanges the authorization code for an access token
        and a refresh token from the Spotify API.
        """
        token_url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'authorization_code',
            'code': self.auth_code,
            'redirect_uri': self.app_credentials['REDIRECT_URI'],
            'client_id': self.app_credentials['CLIENT_ID'],
            'client_secret': self.app_credentials['CLIENT_SECRET']
        }
    
        response = requests.post(token_url, data=payload)
        response_data = response.json()
    
        if 'access_token' in response_data:
            self.access_token = response_data['access_token']
            self.refresh_token = response_data['refresh_token']
        else:
            print("Error obtaining access token:", response_data)

    def refresh_access_token(self):
        """
        Refreshes the Spotify access token using the 
        provided refresh token.
        """
        token_url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.app_credentials['CLIENT_ID'],
            'client_secret': self.app_credentials['CLIENT_SECRET']
        }
        
        response = requests.post(token_url, data=payload)
        response_data = response.json()
        
        if 'access_token' in response_data:
            self.access_token = response_data['access_token']
        else:
            print("Error refreshing access token:", response_data)


    def execute_api_request(self, endpoint, params={}, http_method='GET'):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.access_token
        }
        if http_method=='GET':
            response = requests.get(url = BASE_URL + endpoint, params=params, headers=headers)
        elif http_method=='POST':
            response = requests.post(url = BASE_URL + endpoint, data=params, headers=headers)
        elif http_method=='PUT':
            response = requests.put(url = BASE_URL + endpoint, data=params, headers=headers)
        else:
            print("Error - http_method must be on of: GET, POST, PUT.")

        try:
            if response.status_code != 200:
                raise HTTPError(response.status_code)
            return response
        except:
            return {'Error': 'Issue with request'}


    def get_user_library_tracks(self, offset=0, limit=50):
        """
        Gets a list of tracks saved in the authenticated user's library.
    
        Parameters:
        offset (int): The index of the first track to return. 
                      Defaults to 0.
        limit (int): The maximum number of tracks to return. 
                     Defaults to 50.
    
        Returns:
        list: A list of track objects saved in the user's library.
        """
        endpoint = "me/tracks"
        params = {
            'offset':offset,
            'limit':limit
        }
        response = self.execute_api_request(endpoint, params)
            
        return response.json()['items']

    def get_audio_features_several_tracks(self, track_ids):
        """
        Retrieves audio features for several tracks from the Spotify API.
    
        This function sends a request to the Spotify Web API to get audio
        feature information for a list of track IDs. The audio features 
        include various musical attributes such as tempo, danceability,
        energy, and more.
    
        Parameters:
        track_ids (str): A comma-separated string of Spotify track IDs for 
                         which to retrieve audio features.
    
        Returns:
        list: A list of dictionaries containing the audio features 
              for each track. If the request fails, an error message 
              is returned instead.
        """
        endpoint = "audio-features"
        params = {
            'ids':track_ids,
        }
        response = self.execute_api_request(endpoint, params)
            
        return response.json()['audio_features']

    def get_several_albums(self, album_ids):
        """
        Retrieves information for several albums 
        from the Spotify API.
    
        This function sends a request to the Spotify Web API 
        to get information for multiple albums
        identified by their Spotify IDs.
    
        Parameters:
        album_ids (str): A comma-separated string of Spotify 
                         album IDs for which to retrieve information.
    
        Returns:
        list: A list of dictionaries containing information for 
              each album. If the request fails,
              an HTTPError is raised.
        """
        endpoint = "albums"
        params = {
            'ids':album_ids,
        }
        response = self.execute_api_request(endpoint, params)
        
        if response.status_code != 200:
            raise HTTPError(response.status_code)
            
        return response.json()['albums']


    def get_several_artists(self, artist_ids):
        endpoint = "artists"
        params = {
            'ids':artist_ids,
        }
        response = self.execute_api_request(endpoint, params)
        
        if response.status_code != 200:
            raise HTTPError(response.status_code)
            
        return response.json()['artists']