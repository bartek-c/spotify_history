import pandas as pd
import numpy as np
import math
from itertools import chain

def process_liked_songs(df):
    """
    Cleans dataframe of liked song and
    prepares for analysis.
    """
    df = process_dates(df)
    df = process_durations(df)
    df = reorder_columns(df)
    df = extract_genres(df)

    # might neeed extra bit for getting main genres

    return df
    

def process_dates(df):
    df.date_added = pd.to_datetime(df.date_added)
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    df['time_added'] = df['date_added'].dt.time
    df['day_of_week_added'] = df['date_added'].dt.dayofweek
    
    days_of_week_mapping = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    
    df['day_of_week_added'] = df['day_of_week_added'].apply(lambda x: days_of_week_mapping[x])

    month_mapping = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    
    
    df['month_added'] = df['month_added'].apply(lambda x: month_mapping[x])
    
    df['date_added'] = df['date_added'].dt.date

    return df

def process_durations(df):
    df['duration_ms'] = df['duration_ms'] / 1000
    df = df.rename(columns={'duration_ms':'duration_s'})
    df['duration_min'] = df['duration_s'] / 60
    
    return df

def reorder_columns(df):
    df = df[['id',
     'name',
     'popularity',
     'is_local',
     'is_explicit',
     'danceability',
     'energy',
     'key',
     'loudness',
     'mode',
     'speechiness',
     'acousticness',
     'instrumentalness',
     'liveness',
     'valence',
     'tempo',
     'date_added',
     'year_added',
     'month_added',
     'day_of_week_added',
     'time_added',
     'duration_s',
     'duration_min',
     'album_id',
     'album_name',
     'album_popularity',
     'album_release_date',
     'album_release_date_precision',
     'artist_id',
     'artist_name',
     'artist_popularity',
     'artist_genres']]
    
    return df

def extract_genres(df):
    lists_of_genres = df['artist_genres'].to_list()
    genres = sorted(set(list(chain.from_iterable(lists_of_genres))))

    genres_df = df[['artist_id', 'artist_genres']].copy()

    for genre in genres:
        genres_df[genre] = genres_df['artist_genres'].apply(lambda x: 1 if genre in x else 0)
    genres_df.drop(columns='artist_genres', inplace=True)
    genres_df.drop_duplicates(inplace=True)

    df_clean = pd.merge(df, genres_df, on='artist_id', how='inner')
    df_clean.drop(columns='artist_genres', inplace=True)

    return df_clean