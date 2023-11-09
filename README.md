# NISTADS-data-collection

## Project description
This is a python application that extracts adsorption isotherms data from the NIST adsorption database (https://adsorption.nist.gov/index.php#home) using their dedicated API. The application firstly extracts data regarding adsorbent materials and adsorbate species and generate two separate datasets, then collects the adsorption isotherm experimental data from the database. The dataset of adsorbate species is further modified adding molecular properties (such as molecular weight, canonical smiles, complexity, heavy atoms, etc.) through the PUG REST API (see https://pubchempy.readthedocs.io/en/latest/ for more information). The extracted data is organized in four different tables, which can be eventually saved as .csv files or or injected into any SQL database (see configurations.py):

**- adsorbents data:** data regarding adsorbent materials 

**- adsorbates data:** data regarding adsorbate species

**- single component isotherms:** collection of adsorption isotherm experiments of single component

**- binarey mixture isotherms:** collection of adsorption isotherm experiments of binary mixture


## How to use
Run the main file NISTADS_composer.py and wait until completion. The script may take long time as it has to fetch data for each experiment using a different URL, and it heavily depends on your internet connection performance (more than 20k experiments are available at the time). Using a smaller guest, host of experiments fraction will decrease the estimated time.

### Configurations
The configurations.py file allows to change the script configuration. The following parameters are available:

- `guest_fraction:` fraction of adsorbate species data to be fetched
- `host_fraction:` fraction of adsorbent materials data to be fetched
- `experiments_fraction:` fraction of adsorption isotherm data to be fetched
- `experiments_fraction:` fraction of adsorption isotherm data to be fetched
- `output_type:` select how to save data (CSV for .csv files, SQL for SQL database)
- `SQL_config:` configuration for SQL connection (username and password)

### Requirements
This application has been developed and tested using the following dependencies (Python 3.10.12):

- `art==6.1`
- `pandas==2.0.3`
- `PubChemPy==1.0.4`
- `requests==2.31.0`
- `SQLAlchemy==2.0.22`
- `tqdm==4.66.1`

These dependencies are specified in the provided `requirements.txt` file to ensure full compatibility with the application. 

