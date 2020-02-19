# A simple statistical method for anomaly detection in Gridded Temperature (NCEP-2) data
Detect anomalies in gridded climate data using domain method

Please read the following paper for more information: 
```
@article{ramachandra2016detecting,
  title={Detecting extreme events in gridded climate data},
  author={Ramachandra, Bharathkumar and Gadiraju, Krishna Karthik and Vatsavai, Ranga Raju and Kaiser, Dale P and Karnowski, Thomas P},
  journal={Procedia Computer Science},
  volume={80},
  pages={2397--2401},
  year={2016},
  publisher={Elsevier}
}
```

* ***Note 1***: The code is only for the anomaly detection part
* ***Note 2***: This code makes some assumptions. Such as it ignores leap year day in every leap year to make the computations simpler.

### How to run?
* Step-0: Verify you have all the necessary python packages installed. First install anaconda, followed by using the below commands to first create the conda environment necessary for this project as well as activate it.
 - To create the environment using the environment file supplied in this project: ``` conda env create -f climate.yml```
 - To activate the environment once created (either use conda activate or source activate): ```conda activate climate``` or ```source activate climate```
* Step-1: Verify you have netcdf files from the years 1979-2013 in the data folder (if not, use the ```ncep2data.py``` file to download). If you already have access to these files, ensure that the netcdf files are directly under the data folder. 
* Step 2: Switch to ```anom-detect``` directory and run the command ```jupyter notebook```. Once the browser window opens, click on ``` Demonstrate Anomaly Detection``` ipython notebook. Click run to run each cell. 
