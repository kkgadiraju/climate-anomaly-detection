###############
# Data is in matlab matrices format, load it into memory as numpy array
# Plotting reference: http://earthpy.org/05_Graphs_and_maps_Matplotlib_and_Basemap.html
#############

import scipy as sp
import scipy.stats as st
import netCDF4
import os, glob, sys
import numpy as np
#from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20,10)
from mpl_toolkits.basemap import Basemap
from matplotlib import colors
#colors.DivergingNorm(vmin=-40., vcenter=0., vmax=40.)

def load_data(folder_name, start_year, end_year):
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

    #all_mat_files = glob.glob(os.path.join(folder_name, '*.mat'))

    all_data = None

    for year in range(start_year, end_year + 1):
        mat_file = os.path.join(folder_name, f'air.2m.gauss.{year}.nc')
        if not os.path.exists(mat_file):
            print(f'File {mat_file} does not exists')
            sys.exit(0) 
        f = netCDF4.Dataset(f'../data/air.2m.gauss.{year}.nc')
        # for simplicity sake, ignoring leap year last day
        curr_data = f.variables['air'][:][0:365, :, :, :]
        curr_data = curr_data.reshape((365, 94, 192)) 
        curr_data = curr_data[np.newaxis, :, :, :]
        if all_data is None:
            all_data = np.copy(curr_data)
        else:
            all_data = np.vstack((all_data, curr_data))
    print('Finished loading data into memory...')
    return all_data


def calculate_five_day_window(all_data, day_number):
    """
    Generate 5 day windows necessary to calculate long term means

    """
    curr_window = all_data[:, day_number-2: day_number+3, :, :] # (35, 5, 94, 192)
    curr_window = curr_window.reshape(curr_window.shape[0] * curr_window.shape[1], curr_window.shape[2], curr_window.shape[3]) # (175, 94, 192)
    #plot_data(curr_window[0, :, :], 'coolwarm')
    
    return curr_window    


def plot_data(data, cmap, title, norm=None):

    plt.clf()
    plt.cla() 
    
    m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')#Basemap(resolution='l')
    m.drawcoastlines()
    if norm is not None:
        img = m.imshow(np.flip(data, 0), interpolation='None', cmap=cmap, norm=norm)
    else:
        img = m.imshow(np.flip(data, 0), interpolation='None', cmap=cmap) 
    m.colorbar(img)
    #plt.show() 
    #plt.savefig(f'./{i}.png')
    plt.title(title)
    plt.show()
    

def plot_heatmap(data, day_number, year_number):
    day = data[year_number, day_number, :, :]
    plot_data(day, 'coolwarm', 'Surface Temperature Heat Map') 
    

def plot_anomalies(data, day_number, year_number):
    # Reference: https://matplotlib.org/3.1.1/gallery/userdemo/colormap_normalizations_custom.html
    class MidpointNormalize(colors.Normalize):
        def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
            self.midpoint = midpoint
            colors.Normalize.__init__(self, vmin, vmax, clip)

        def __call__(self, value, clip=None):
            # I'm ignoring masked values and all kinds of edge cases to make a
            # simple example...
            x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
            return np.ma.masked_array(np.interp(value, x, y))
    norm=MidpointNormalize(midpoint=0.)
    plot_data(data, 'coolwarm', f'Anomalies for day#{day_number} in year#{year_number}', norm)


def detect_anomalies(all_data, day_number, year_number, percentile):
    """

    """
    curr_long_term_window = calculate_five_day_window(all_data, day_number) # 175 * 94 * 192 (35 years,5 days per year) 
    curr_long_term_mean = np.mean(curr_long_term_window, axis = 0) # 94 * 192
    curr_long_term_std = np.std(curr_long_term_window, axis = 0) # 94 * 192
    z_score = st.norm.ppf(percentile)
    max_lim = curr_long_term_mean + z_score * curr_long_term_std
    min_lim = curr_long_term_mean - z_score * curr_long_term_std
    #print(curr_long_term_mean, curr_long_term_std, max_lim, min_lim)
    # calculate anomaly score for specific year
    curr_day = all_data[year_number, day_number, :, :]
    heat_anomaly_mask = (curr_day > max_lim)
    cold_anomaly_mask = (curr_day < min_lim)
    final_mask = np.zeros(heat_anomaly_mask.shape)
    anomaly_score = curr_day - curr_long_term_mean
    final_mask[heat_anomaly_mask] = anomaly_score[heat_anomaly_mask]
    final_mask[cold_anomaly_mask] = anomaly_score[cold_anomaly_mask]
    #print(f'Number of hot anomalies = {np.sum(heat_anomaly_mask)}, cold anomalies = {np.sum(cold_anomaly_mask)}') 
    #cmap = colors.ListedColormap(['blue', 'white', 'red'])
    plot_anomalies(final_mask, day_number, year_number)

if __name__=="__main__":
    all_data = load_data('../data/', 1979, 2013) # n_years * 365 * 94 * 192
    for i in range(193, 203):
        detect_anomalies(all_data, i, 31, 0.99)
    plot_heatmap(all_data, 200, 24)
