Example
========

Walkthrough for an example case on Linux system:
The example directory includes randomly drawn polygons (example_parcels.shp) and Sentinel2 tiles over Finland (Fin_s2.shp, derived from xx).
The data in cropyield/example/cropyield_data is only intended for testing purposes.

| According to chapter **Preparation**:

1. Download conda : `` wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh ``
2. Install above downloaded
3. Create conda environment with required packages: `` conda env create --file environment.yml ``
4. Activate above created environment: `` conda activate cropyield ``

| According to chapter **Usage**:

5. Clone the repository: `` git clone https://github.com/myliheik/cropyield.git ``
6. Switch into repository directory : `` cd cropyield ``
7. Switch to example directory: `` cd example/cropyield_data/S2 ``
8. Get the data with: `` wget https://a3s.fi/Sentinel2testCase/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE.tar.zst ``, and unpack with `` tar -I zstd -xvf S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE.tar.zst ``, then switch back to example directory by typing `` cd .. `` twice.
9. Split test-shapefile based on S2 tiles (here only Finland): `` python ../python/splitshp_mp.py ../example/cropyield_data/example_parcels.shp ../example/cropyield_data/Fin_s2.shp ../example/cropyield_shp``
10. Start the process (for the example use the start file within example directory) `` bash start.sh ``
11. Check the result files in ./cropyield_results

Resulting files:
-----------------

* Step 9 should create files within cropyield_shp: All tiles here have overlap with the example_parcels file: 34VEN,34VFN,34VFP,35VLH,35VLJ.

* Step 10 should create 2 files in cropyield_results (plus some resampled shapefiles in cropyield_data):
    * array_34VFN_20200626_B04.csv with PlotID as first row following all pixelvalues within each polygon, and
    * meta_34VFN_20200626_B04.csv with PlotID,year,DOY,tilefilename,missionID,count for each polygon.

-> if those files exist and are non empty, everything is fine. If not check the error messages and that all inputs are available.
