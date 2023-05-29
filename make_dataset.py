import pandas as pd
import numpy as np

def start_pipeline(dataf):
    """Starts the data pipeline"""
    return dataf.copy()

def convert_to_datetime(dataf):
    """Formats the date column"""
    dataf['date_'] = pd.to_datetime(dataf['date_'])
    dataf['date_'] = dataf['date_'].apply(lambda t: t.replace(tzinfo=None))
    dataf['date_'] = dataf['date_'].astype('datetime64[ns]')
    dataf['time'] = pd.to_datetime(dataf['time'], format='%H:%M:%S').dt.time

    return dataf

def add_time_series_features(dataf):
    """Format the date column and add features to the dataset"""
    dataf['weekday'] = dataf['date_'].dt.weekday
    dataf['week_no'] = dataf['date_'].dt.isocalendar().week
    dataf['month'] = dataf['date_'].dt.month
    dataf['month_name'] = dataf['date_'].dt.month_name()
    dataf['day_name'] = dataf['date_'].dt.day_name()
    dataf['day'] = dataf['date_'].dt.day
    dataf['hour'] = dataf['time'].apply(lambda x: x.hour)
    return dataf

def add_features(dataf):
    """Adds features to the dataset"""
    dataf['victim_outcome'] = np.where(dataf['fatal'] == 1, 'Fatal', 'Non-fatal')
    dataf['non_fatal'] = np.where(dataf['fatal'] == 0, 1, 0)
    dataf['shooting_incidents'] = np.where(dataf['objectid'] > 0, 1, 0)
    return dataf

def drop_missing_dist(dataf):
    """Drops rows where 'dist' is missing"""
    dataf = dataf.dropna(subset=['dist'])
    return dataf

# def fill_missing_values(dataf):
#     """Fills missing values"""
#     dataf['dist'] = dataf['dist'].fillna(0.0)
#     return dataf
    