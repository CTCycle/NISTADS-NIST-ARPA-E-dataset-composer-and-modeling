import os
from tqdm import tqdm
tqdm.pandas()

# ...
#==============================================================================
#==============================================================================
#==============================================================================
class UserOperations:
    
    """    
    A class for user operations such as interactions with the console, directories and files
    cleaning and other maintenance operations.
      
    Methods:
        
    menu_selection(menu):  console menu management 
    clear_all_files(path): remove files and directories
   
    """
    
    # print custom menu on console and allows selecting an option
    #==========================================================================
    def menu_selection(self, menu):        
        
        """        
        menu_selection(menu)
        
        Presents a custom menu to the user and returns the selected option.
        
        Keyword arguments:                      
            menu (dict): A dictionary containing the options to be presented to the user. 
                         The keys are integers representing the option numbers, and the 
                         values are strings representing the option descriptions.
        
        Returns:            
            op_sel (int): The selected option number.
        
        """        
        indexes = [idx + 1 for idx, val in enumerate(menu)]
        for key, value in menu.items():
            print('{0} - {1}'.format(key, value))            
        
        print()
        while True:
            try:
                op_sel = int(input('Select the desired operation: '))
            except:
                continue            
            
            while op_sel not in indexes:
                try:
                    op_sel = int(input('Input is not valid, please select a valid option: '))
                except:
                    continue
            break
        
        return op_sel        


# define the class for inspection of the input folder and generation of files list.
#==============================================================================
#==============================================================================
#==============================================================================
class AdsorptionDataset:
    
    '''   
    A class collecting methods to build the NIST adsorption dataset from collected
    data. Methods are meant to be used sequentially as they are self-referring 
    (no need to specify input argument in the method). 
      
    Methods:
        
    extract_molecular_properties(df_mol):  retrieve molecular properties from ChemSpyder
    split_by_mixcomplexity():              separates single component and binary mixture measurements
    extract_adsorption_data():             retrieve molecular properties from ChemSpyder    
    
    '''
    def __init__(self, dataframe):
        self.dataframe = dataframe      
    
    #==========================================================================           
    def split_by_mixcomplexity(self):   

        '''
        split_by_mixcomplexity()

        Splits the dataframe into two groups based on the number of adsorbates.
        This function adds a new column 'num_of_adsorbates' to the dataframe, 
        which contains the number of adsorbates for each row. The dataframe is then 
        grouped by this column and split into two groups: one group with a single adsorbate 
        and another group with two adsorbates. If either of these groups is empty, 
        its value is set to 'None'.

        Returns:
            tuple: A tuple containing two dataframes, one for each group (single_compound, binary_mixture)
        
        '''       
        self.dataframe['num_of_adsorbates'] = self.dataframe['adsorbates'].apply(lambda x : len(x))          
        grouped_df = self.dataframe.groupby('num_of_adsorbates')
        try:
            single_compound = grouped_df.get_group(1)
        except:
            single_compound = 'None'
        try:
            binary_mixture = grouped_df.get_group(2)
        except:
            binary_mixture = 'None'        
        
        return single_compound, binary_mixture      
      
    
    #==========================================================================
    def extract_adsorption_data(self, raw_data, num_species=1): 

        '''
        extract_adsorption_data()

        Extracts adsorption data from the single_compound and binary_mixture dataframes.
        This function creates two new dataframes, df_SC and df_BN, as copies of the single_compound and 
        binary_mixture dataframes, respectively. It then extracts various pieces of information from 
        these dataframes, such as the adsorbent ID and name, the adsorbates ID and name, and the pressure 
        and adsorbed amount data. For the binary mixture dataframe, it also calculates the composition and 
        pressure of each compound.

        Returns:
            tuple: A tuple containing two dataframes with the extracted adsorption data (df_SC, df_BN)
        
        '''  
        df_adsorption = raw_data.copy()
        if num_species==1:                             
            df_adsorption['adsorbent_ID'] = df_adsorption['adsorbent'].apply(lambda x : x['hashkey'])      
            df_adsorption['adsorbent_name'] = df_adsorption['adsorbent'].apply(lambda x : x['name'])           
            df_adsorption['adsorbates_ID'] = df_adsorption['adsorbates'].apply(lambda x : [f['InChIKey'] for f in x])            
            df_adsorption['adsorbates_name'] = df_adsorption['adsorbates'].apply(lambda x : [f['name'] for f in x][0])
            df_adsorption['pressure'] = df_adsorption['isotherm_data'].apply(lambda x : [f['pressure'] for f in x])                
            df_adsorption['adsorbed_amount'] = df_adsorption['isotherm_data'].apply(lambda x : [f['total_adsorption'] for f in x])
            df_adsorption['composition'] = 1.0 

        elif num_species==2:            
            df_adsorption['adsorbent_ID'] = df_adsorption['adsorbent'].apply(lambda x : x['hashkey'])           
            df_adsorption['adsorbent_name'] = df_adsorption['adsorbent'].apply(lambda x : x['name'])               
            df_adsorption['adsorbates_ID'] = df_adsorption['adsorbates'].apply(lambda x : [f['InChIKey'] for f in x])          
            df_adsorption['adsorbates_name'] = df_adsorption['adsorbates'].apply(lambda x : [f['name'] for f in x])         
            df_adsorption['total_pressure'] = df_adsorption['isotherm_data'].apply(lambda x : [f['pressure'] for f in x])                
            df_adsorption['all_species_data'] = df_adsorption['isotherm_data'].apply(lambda x : [f['species_data'] for f in x])              
            df_adsorption['compound_1_data'] = df_adsorption['all_species_data'].apply(lambda x : [f[0] for f in x])               
            df_adsorption['compound_2_data'] = df_adsorption['all_species_data'].apply(lambda x : [f[0] for f in x])            
            df_adsorption['compound_1_composition'] = df_adsorption['compound_1_data'].apply(lambda x : [f['composition'] for f in x])              
            df_adsorption['compound_2_composition'] = df_adsorption['compound_2_data'].apply(lambda x : [f['composition'] for f in x])            
            df_adsorption['compound_1_pressure'] = df_adsorption.apply(lambda x: [a * b for a, b in zip(x['compound_1_composition'], x['total_pressure'])], axis=1)             
            df_adsorption['compound_2_pressure'] = df_adsorption.apply(lambda x: [a * b for a, b in zip(x['compound_2_composition'], x['total_pressure'])], axis=1)                
            df_adsorption['compound_1_adsorption'] = df_adsorption['compound_1_data'].apply(lambda x : [f['adsorption'] for f in x])               
            df_adsorption['compound_2_adsorption'] = df_adsorption['compound_2_data'].apply(lambda x : [f['adsorption'] for f in x])
                                    
        return df_adsorption         
    
    #==========================================================================
    def dataset_expansion(self, df_SC, df_BM):

        '''
        dataset_expansion()

        Expands the datasets by exploding and dropping columns.

        Returns:
            SC_exploded_dataset (DataFrame): The expanded single-component dataset.
            BN_exploded_dataset (DataFrame): The expanded binary-component dataset.

        '''       
        df_single = df_SC.copy()
        df_binary = df_BM.copy()       
                         
        explode_cols = ['pressure', 'adsorbed_amount']
        drop_columns = ['DOI', 'date', 'adsorbent', 'concentrationUnits', 
                        'adsorbates', 'isotherm_data', 'adsorbent_ID', 'adsorbates_ID']
        
        SC_exp_dataset = df_single.explode(explode_cols)
        SC_exp_dataset.reset_index(inplace = True, drop = True)       
        SC_exploded_dataset = SC_exp_dataset.drop(columns = drop_columns)        
        df_binary['compound_1'] = df_binary['adsorbates_name'].apply(lambda x : x[0])        
        df_binary['compound_2'] = df_binary['adsorbates_name'].apply(lambda x : x[1])        
        
        explode_cols = ['compound_1_pressure', 'compound_2_pressure',
                        'compound_1_adsorption', 'compound_2_adsorption']
        drop_columns = ['DOI', 'date', 'adsorbates_name', 'adsorbent', 'concentrationUnits',
                        'all_species_data', 'compound_1_data', 'compound_2_data',
                        'adsorbates', 'isotherm_data', 'adsorbent_ID', 'adsorbates_ID']
        
        BM_exp_dataset = df_binary.explode(explode_cols)       
        BM_exp_dataset.reset_index(inplace = True, drop = True)        
        BM_exploded_dataset = BM_exp_dataset.drop(columns = drop_columns) 
        
        SC_exploded_dataset.dropna(inplace = True)
        BM_exploded_dataset.dropna(inplace = True)        
        
        return SC_exploded_dataset, BM_exploded_dataset
    
    
# define the class for inspection of the input folder and generation of files list.
#==============================================================================
#==============================================================================
#==============================================================================
class DataStorage: 

    #==========================================================================
    def JSON_serializer(self, object, filename, path, mode='SAVE'):

        if mode == 'SAVE':
            object_json = object.to_json()          
            json_path = os.path.join(path, f'{filename}.json')
            with open(json_path, 'w', encoding = 'utf-8') as f:
                f.write(object_json)
        elif mode == 'LOAD':
            pass

    



        