###############
# Data is in matlab matrices format, load it into memory as numpy array
# Plotting reference: http://earthpy.org/05_Graphs_and_maps_Matplotlib_and_Basemap.html
#############
from scipy.io import loadmat
import scipy.stats as st
import netCDF4
import os, glob, sys
import numpy as np
#from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import colors

def load_data(start_year, end_year):
    """
    Load data stored in data folder in specified range
    
    Load data in the range specified between the years start_year and end_year (inclusive of both years)
   
    Original data is stored in the form of number of days in year * nrows * ncols (where nrows * ncols refers to the number of rows and columns in the gridded climate data)

    Since this is a purely temporal solution, we flatten the last two dimensions

    Also, for the sake of simplicity, we ignore the last day of leap years

    Parameters
    ----------
    start_year: int
              An integer indicating the first year to take
    end_year: int
              An integer indicating the last year to take
    
    Returns
    --------
    numpy.ndarray: A floating point array containing the information for all the years under consideration. Of the format (end_year - start_year +_ 1) * 365 * 10512

    """
    mat_folder_name = '../data/'
    csv_folder_name = '../data/csv/'

    #all_mat_files = glob.glob(os.path.join(mat_folder_name, '*.mat'))

    all_data = None

    for year in range(start_year, end_year + 1):
        mat_file = os.path.join(mat_folder_name, f'air.2m.gauss.{year}.nc')
        if not os.path.exists(mat_file):
            print(f'File {mat_file} does not exists')
            sys.exit(0) 
        f = netCDF4.Dataset(f'../data/air.2m.gauss.{year}.nc')
        #print(f.variables['air'][:].shape)
        #print(f.variables['lat'][:].shape)
        curr_lats = f.variables['lat'][:]
        curr_longs = f.variables['lon'][:]                               
        # for simplicity sake, ignoring leap year last day
        curr_data = f.variables['air'][:][0:365, :, :, :]
        curr_data = curr_data.reshape((365, 94, 192)) 
        curr_data = curr_data[np.newaxis, :, :, :]
        if all_data is None:
            all_data = np.copy(curr_data)
        else:
            all_data = np.vstack((all_data, curr_data))
    print('Finished loading data into memory...')
    return [all_data, curr_lats, curr_longs]


def calculate_five_day_window(all_data, day_number):
    """
    Generate 5 day windows necessary to calculate long term means

    """
    curr_window = all_data[:, day_number-2: day_number+3, :, :] 
    curr_window = curr_window.reshape(curr_window.shape[0] * curr_window.shape[1], curr_window.shape[2], curr_window.shape[3])
    return curr_window    


def plot_data(data, cmap):
    m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')#Basemap(resolution='l')
    m.drawcoastlines()
    img = m.imshow(np.flip(data, 0), interpolation='None', cmap=cmap)
    m.colorbar(img)
    plt.show() 


def calculate_anomaly_score(all_data, day_number, year_number, percentile, longs, lats):
    """

    """
    curr_long_term_window = calculate_five_day_window(all_data, day_number)
    curr_long_term_mean = np.mean(curr_long_term_window, axis = 0)
    curr_long_term_std = np.std(curr_long_term_window, axis = 0)
    z_score = st.norm.ppf(percentile)
    #print(f'Zscore for {percentile} percentile is {z_score}')
    max_lim = curr_long_term_mean + z_score * curr_long_term_std
    min_lim = curr_long_term_mean - z_score * curr_long_term_std
    #print(curr_long_term_mean, curr_long_term_std, max_lim, min_lim)
    # calculate anomaly score for specific year
    curr_day = all_data[year_number, day_number, :, :]
    heat_anomaly_mask = (curr_day > max_lim)
    cold_anomaly_mask = (curr_day < min_lim)
    final_mask = np.zeros(heat_anomaly_mask.shape)
    final_mask[heat_anomaly_mask] = 1
    final_mask[cold_anomaly_mask] = -1
    print(f'Number of hot anomalies = {np.sum(heat_anomaly_mask)}, cold anomalies = {np.sum(cold_anomaly_mask)}') 
    cmap = colors.ListedColormap(['blue', 'white', 'red'])
    plot_data(final_mask, cmap)
    '''
    m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')#Basemap(resolution='l')
    #X,Y = m(lons2, lats2)
    #m.drawcountries()
    m.drawcoastlines()
    #m.contourf(X, Y, final_mask)
    img = m.imshow(final_mask, interpolation='None')#, cmap=cmap)
    m.colorbar(img)
    plt.show() 
    '''         

if __name__=="__main__":
    all_data, lats, longs = load_data(1990, 2019)
    print(all_data.shape, lats.shape, longs.shape)
    calculate_anomaly_score(all_data, 204, 14, 0.95, longs, lats)
    #plot_data(all_data[13, 204, :, :], 'Reds') 
    #print(np.min(lats), np.max(lats), np.min(longs), np.max(longs))
