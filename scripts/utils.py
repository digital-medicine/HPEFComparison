"""
===================================================================
Title:          utils.py
Description:    Collection of recurring functions
Authors:        Maximilian Kapsecker and Fabian Kahl
===================================================================
"""

import numpy as np
from scipy.stats import pearsonr
from scipy import stats
import os
import pandas as pd

def extract_coordinates(df, col_name):
    """Extracts the coordinates (X, Y, Z) based on the provided joint (=column name)."""
    data = df[[col_name+"X", col_name+"Y", col_name+"Z"]]
    return np.array(data)

def vectors(A, B, C):
    """Returns the vectors generated BA and BC based on (A, B , C)."""
    vec1 = A-B
    vec2 = C-B
    return vec1, vec2

def calculate_angles(vec1, vec2):
    """Calculates the angles of two vectors in degree."""
    inv_cos = np.dot(vec1, vec2) / (np.linalg.norm(vec1)*np.linalg.norm(vec2))
    return np.rad2deg(np.arccos(inv_cos))

def cut_timeseries(series_a, series_b):
    # Find indices where either array has NaN
    nan_indices = np.isnan(series_a) | np.isnan(series_b)
    
    # Remove the corresponding elements from both arrays
    series_a = series_a[~nan_indices]
    series_b = series_b[~nan_indices]

    return series_a, series_b

def baseline_drift(series_a, series_b):
    
    abs_difference_min = np.mean(np.abs(np.array(series_a) - np.array(series_b)))
    best_k = 0

    for k in range(-90, 90):
        abs_difference = np.mean(np.abs((np.array(series_a) + k) - np.array(series_b)))
        
        if abs_difference_min > abs_difference:
            best_k = k
            abs_difference_min = abs_difference

    return best_k, abs_difference_min

def compute_angles(df, names, mapping, ipad_view='Frontal', subject=1, exercise='Squat'):
    '''
    Computes the angles for vicon and framework data for a specific configuration (angle, view, subject, exercise)
    '''
    config = {
        'angles': names,
        'iPad view': ipad_view,
        'subject': subject,
        'exercise': exercise,
    }
    
    a = names[0]
    b = names[1]
    c = names[2]
    mask = (df['ipad_view'] == ipad_view) & (df['subject'] == 'Sub' + str(subject)) & (df['exerciseName'] == exercise)
    df = df[mask]
    
    a_ar = np.array(df[[a + 'X', a + 'Y', a + 'Z']], dtype=float)
    b_ar = np.array(df[[b + 'X', b + 'Y', b + 'Z']], dtype=float)
    c_ar = np.array(df[[c + 'X', c + 'Y', c + 'Z']], dtype=float)
    
    a_vi = np.array(df[[mapping[a] + '_X_mm', mapping[a] + '_Y_mm', mapping[a] + '_Z_mm']], dtype=float)
    b_vi = np.array(df[[mapping[b] + '_X_mm', mapping[b] + '_Y_mm', mapping[b] + '_Z_mm']], dtype=float)
    c_vi = np.array(df[[mapping[c] + '_X_mm', mapping[c] + '_Y_mm', mapping[c] + '_Z_mm']], dtype=float)
    
    vectors_ar = vectors(a_ar, b_ar, c_ar)
    vectors_vi = vectors(a_vi, b_vi, c_vi)
        
    n = len(df)
    angles_ar = [calculate_angles(vectors_ar[0][i], vectors_ar[1][i]) for i in range(n)]
    angles_vi = [calculate_angles(vectors_vi[0][i], vectors_vi[1][i]) for i in range(n)]

    return np.array(angles_ar), np.array(angles_vi), config

def compute_vicon_angles(df, names, mapping):
    '''
    Computes the angles for vicon data for a specific configuration (angle, view, subject, exercise)
    '''
    config = {
        'angles': names,
    }
    
    a = names[0]
    b = names[1]
    c = names[2]
        
    a_vi = np.array(df[[mapping[a] + '_X_mm', mapping[a] + '_Y_mm', mapping[a] + '_Z_mm']], dtype=float)
    b_vi = np.array(df[[mapping[b] + '_X_mm', mapping[b] + '_Y_mm', mapping[b] + '_Z_mm']], dtype=float)
    c_vi = np.array(df[[mapping[c] + '_X_mm', mapping[c] + '_Y_mm', mapping[c] + '_Z_mm']], dtype=float)
    
    vectors_vi = vectors(a_vi, b_vi, c_vi)
        
    n = len(df)
    angles_vi = [calculate_angles(vectors_vi[0][i], vectors_vi[1][i]) for i in range(n)]

    return np.array(angles_vi), config
    
def fill_array(arr):
    try:
        mask = np.isnan(arr)
        arr[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), arr[~mask]
                              , left=np.nan, right=np.nan)
        return arr
    except:
        return arr

def pearsonr_ci(x,y,alpha=0.05):
    ''' calculate Pearson correlation along with the confidence interval using scipy and numpy
    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default
    Returns
    -------
    r : float
      Pearson's correlation coefficient
    pval : float
      The corresponding p value
    r_z : float
      The z-Transform of r
    lo, hi : float
      The lower and upper bound of confidence intervals
    '''

    r, p = stats.pearsonr(x,y)
    r_z = np.arctanh(r)
    se = 1/np.sqrt(x.size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    lo, hi = np.tanh((lo_z, hi_z))
    return r, p, r_z, lo, hi



def spearmanr_ci(x,y,alpha=0.05):
    ''' calculate Pearson correlation along with the confidence interval using scipy and numpy
    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default
    Returns
    -------
    r : float
      Pearson's correlation coefficient
    pval : float
      The corresponding p value
    r_z : float
      The z-Transform of r
    lo, hi : float
      The lower and upper bound of confidence intervals
    '''
    
    r, p = stats.spearmanr(x,y)
    r_z = np.arctanh(r)
    se = 1/np.sqrt(x.size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    lo, hi = np.tanh((lo_z, hi_z))
    return r, p, r_z, lo, hi

def weighted_avg_and_std(values, weights):
    # Source: https://stackoverflow.com/questions/2413522/weighted-standard-deviation-in-numpy
    """
    Return the weighted average and standard deviation.
    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return str(np.round(average, 2)) + " ± " + str(np.round(np.sqrt(variance),2))

def weighted_avg(values, weights):
    # Source: https://stackoverflow.com/questions/2413522/weighted-standard-deviation-in-numpy
    """
    Return the weighted average and standard deviation.
    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    return np.round(average, 2)

def generate_vicon_column_set(mapping):
    """Generates the corresponding Vicon column names based on general column names."""
    columns = ['default_Frame_nan']
    for k in mapping:
        columns.append(mapping[k] + '_X_mm')
        columns.append(mapping[k] + '_Y_mm')
        columns.append(mapping[k] + '_Z_mm')
    return columns

def generate_framework_column_set(mapping):
    """Generates the relevant framework column names."""
    columns = []
    columns.append('timestamp')
    columns.append('exerciseName')
    columns.append('ipad_view')
    columns.append('subject')
    
    for k in mapping:
        columns.append(k + 'X')
        columns.append(k + 'Y')
        columns.append(k + 'Z')

    return columns

def start_to_end(file):
    """Opens the xcp file (Vicon metadata) and extracts start- and endtime of recording."""
    with open(file[:-3] + 'xcp') as f:
        lines = f.readlines()
        # TODO: can be done more dynamic with a search for the first occurence of the key <Capture .. >
        try:
            starttime = pd.to_datetime(lines[6][92:115])
            endtime = pd.to_datetime(lines[6][36:59])
        except:
            starttime = pd.to_datetime(lines[7][134:157])
            endtime = pd.to_datetime(lines[7][36:59])
    return starttime, endtime

def list_files(startpath):
    """Returns file structure in the specified directory."""
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def drop_unnecessary_elements(lst, substrings):
    # Drop all elements not in substrings
    return [item for item in lst if any(substring.lower() in item.lower() for substring in substrings)]

def align_timeseries(series_a, series_b, range_field = 60):
    '''Aligning two timely shifted timeseries by looking for maximum cross correlation by time lags'''
    
    # Interpolate the timeseries (no extrapolating!)
    series_a = fill_array(series_a)
    series_b = fill_array(series_b)
    
    # Find indices where at least one array has NaN
    nan_indices = np.isnan(series_a) | np.isnan(series_b)

    # Remove the corresponding elements from both arrays
    series_a = series_a[~nan_indices]
    series_b = series_b[~nan_indices]
            
    # Correlation without shift
    corr_max, _ = pearsonr(
        series_a[(range_field):(-range_field)],
        series_b[range_field:-range_field]
    )
    best_k = 0
    
    for k in range(-range_field, range_field):
        corr, _ = pearsonr(
            series_a[(range_field + k):(-range_field + k)],
            series_b[range_field:-range_field]
        )
        if corr_max < corr:
            best_k = k
            corr_max = corr
    return best_k

def shift_timeseries(series_a, series_b, shift_value):
    '''Shifting two timely shifted timeseries by shifting by fixed frame number'''

    # Interpolate the timeseries (no extrapolating!)
    series_a = fill_array(series_a)
    series_b = fill_array(series_b)
    
    if shift_value > 0:
        # Pad the array with nans on the left
        series_b = np.pad(series_b, (shift_value, 0), mode='constant',
                          constant_values=(np.nan, np.nan))
        # Pad the array with nans on the right
        series_a = np.pad(series_a, (0, shift_value), mode='constant',
                          constant_values=(np.nan, np.nan))
    if shift_value < 0:
        # Pad the array with nans on the left
        series_a = np.pad(series_a, (-shift_value, 0), mode='constant',
                          constant_values=(np.nan, np.nan))
        # Pad the array with nans on the right
        series_b = np.pad(series_b, (0, -shift_value), mode='constant',
                          constant_values=(np.nan, np.nan))
    
    # Find indices where both array have NaN
    nan_indices = np.isnan(series_a) & np.isnan(series_b)
    
    # Remove the corresponding elements from both arrays
    series_a = series_a[~nan_indices]
    series_b = series_b[~nan_indices]

    return series_a, series_b