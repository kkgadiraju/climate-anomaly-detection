####
## Download daily avg surface temperatures 
## Data will be in netcdf format
## Reference: https://stackoverflow.com/questions/11768214/python-download-a-file-over-an-ftp-server/12424311
###

import shutil
import urllib.request as request
from contextlib import closing
for i in range(1979,2014):
    path = "ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis2.dailyavgs/gaussian_grid/air.2m.gauss."+str(i)+".nc"
    print(f'Downloading {path}')
    with closing(request.urlopen(path)) as r:
        with open("./air.2m.gauss."+str(i)+".nc", 'wb') as f:
            shutil.copyfileobj(r, f)
