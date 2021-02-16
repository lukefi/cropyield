Preparation
============

Linux system (Windows with linux subsystem may work but no support is offered for that). Testing done on Ubuntu 16.04, with Python 2.7 and 3.7 and Anaconda 4.6.14 and CSC's Puhti computing cluster with geoconda module.


Workstation
------------

| Python libraries used:

* os 
* sys
* csv
* shutil
* subprocess
* argparse
* datetime
* numpy
* rasterstats
* gdal
* shapely
* fiona

Some of above mentioned are not default libraries and have to be installed separately.
Creating an `Anaconda <https://www.anaconda.com/>`_ environment is suggested. A .yml file is included in the repository of which a new environment can be created. 

Run ``conda env create -f environment.yml`` to create the environment.
See `here <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ for more information on the topic.
