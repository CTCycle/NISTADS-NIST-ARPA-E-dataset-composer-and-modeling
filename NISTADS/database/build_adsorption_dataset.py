# [SET KERAS BACKEND]
import os 

# [IMPORT LIBRARIES]
import pandas as pd

# [SETTING WARNINGS]
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# [IMPORT CUSTOM MODULES]
from NISTADS.commons.utils.dataloader.serializer import DataSerializer
from NISTADS.commons.utils.process.sanitizer import AdsorptionDataSanitizer
from NISTADS.commons.utils.process.splitting import TrainValidationSplit
from NISTADS.commons.utils.process.normalization import FeatureNormalizer
from NISTADS.commons.utils.process.sequences import PressureUptakeSeriesProcess, SMILETokenization
from NISTADS.commons.utils.process.aggregation import merge_all_datasets, aggregate_adsorption_measurements
from NISTADS.commons.utils.process.conversion import units_conversion
from NISTADS.commons.utils.process.sequences import PressureUptakeSeriesProcess
from NISTADS.commons.constants import CONFIG, DATA_PATH
from NISTADS.commons.logger import logger


# [RUN MAIN]
###############################################################################
if __name__ == '__main__':

    # 1. [LOAD DATA]
    #--------------------------------------------------------------------------     
    # load data from csv, retrieve and merge molecular properties 
    logger.info(f'Loading NISTADS datasets from {DATA_PATH}')
    dataserializer = DataSerializer(CONFIG)
    adsorption_data, guests_data, hosts_data = dataserializer.load_datasets() 
    logger.info(f'{adsorption_data.shape[0]} measurements in the dataset')
    logger.info(f'{guests_data.shape[0]} total guests (adsorbates species) in the dataset')
    logger.info(f'{hosts_data.shape[0]} total hosts (adsorbent materials) in the dataset')

    # 2. [PREPROCESS DATA]
    #--------------------------------------------------------------------------     
    # exlude all data outside given boundaries, such as negative temperature values 
    # and pressure and uptake values below or above the given boundaries
    sanitizer = AdsorptionDataSanitizer(CONFIG)
    processed_data = sanitizer.exclude_outside_boundary(adsorption_data)

    # group data from single measurements based in the experiments  
    # merge adsorption data with materials properties (guest and host) 
    processed_data = aggregate_adsorption_measurements(processed_data)
    processed_data = merge_all_datasets(processed_data, guests_data, hosts_data)   

    # convert and normalize pressure and uptake units:
    # pressure to Pascal, uptake to mol/g
    sequencer = PressureUptakeSeriesProcess(CONFIG)
    processed_data = units_conversion(processed_data)     

    # rectify sequences of pressure/uptake points through following steps:
    # remove repeated zero values at the beginning of the series  
    # sanitize experiments removing those where measurements number is outside acceptable values 
    processed_data = sequencer.remove_leading_zeros(processed_data)   
    processed_data = sequencer.filter_by_sequence_size(processed_data) 
    processed_data = sequencer.PQ_series_padding(processed_data)
    processed_data = sequencer.series_normalization(processed_data)
    processed_data = sequencer.convert_to_values_string(processed_data)   

    # 3. [PROCESS MOLECULAR INPUTS]
    #--------------------------------------------------------------------------  
    tokenization = SMILETokenization(CONFIG)    
    tokenized_data, smile_vocabulary = tokenization.process_SMILE_data(processed_data)

    # 4. [SPLIT BASED NORMALIZATION]
    #-------------------------------------------------------------------------- 
    splitter = TrainValidationSplit(CONFIG, tokenized_data)    
    normalizer = FeatureNormalizer(CONFIG) 
    train_data, validation_data = splitter.split_train_and_validation()
    tokenized_data = normalizer.normalize_molecular_features(tokenized_data, train_data)     

    # 5. [SAVE PREPROCESSED DATA]
    #--------------------------------------------------------------------------
    # save preprocessed data using data serializer       
    dataserializer.save_preprocessed_data(tokenized_data, smile_vocabulary)












