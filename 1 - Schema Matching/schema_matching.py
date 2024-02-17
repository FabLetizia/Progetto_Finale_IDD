import pickle
import os
import pandas as pd
from flexmatcher import FlexMatcher
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")   # LogisticRegression non converge, eliminati i warnings per alleggerire il Prompt

### ################# ###
### SUPPORT FUNCTIONS ###
### ################# ###
def remove_columns(data, columns_to_remove):
    """
    Remove specified columns from the DataFrame.

    Parameters:
    - data: pandas DataFrame
    - columns_to_remove: list of column names to be removed

    Returns:
    - Modified DataFrame without the specified columns
    """
    data.drop(columns=columns_to_remove, errors='ignore', inplace=True)
    return data

def prepare_training_set(folder):
    # SOURCE 1
    data1 = pd.read_csv(folder+'FR-forbes.csv', dtype='object')
    columns_to_remove_data1 = ['Revenue']
    data1 = remove_columns(data1, columns_to_remove_data1)

    # SOURCE 2
    data2 = pd.read_csv(folder+'MarScoToc-AmbitionBox.csv', dtype='object')
    columns_to_remove_data2 = ['Ownership']
    data2 = remove_columns(data2, columns_to_remove_data2)

    # SOURCE 3
    data3 = pd.read_csv(folder+'DDD-cbinsight.csv', dtype='object')
    columns_to_remove_data3 = ['dateJoined', 'investors', 'stage', 'totalRaised']
    data3 = remove_columns(data3, columns_to_remove_data3)

    # SOURCE 4
    data4 = pd.read_csv(folder+'iGMM-companiesMarketCap.csv', dtype='object')
    columns_to_remove_data4 = ['code', 'rank', 'change(1day)', 'change(1year)']
    data4 = remove_columns(data4, columns_to_remove_data4)

    # SOURCE 5
    data5 = pd.read_csv(folder+'wissel-companiesMarketCap.csv', dtype='object')
    columns_to_remove_data5 = ['ID', 'URL', 'Company code', 'Earnings', 'Revenue', 'Shares', 'Employees']
    data5 = remove_columns(data5, columns_to_remove_data5)

    return (data1, data2, data3, data4, data5)

def train_flexmatcher(dataframes, random_state, save=False):
    schema_list = [dataframes[0], dataframes[1], dataframes[2], dataframes[3], dataframes[4]]
    lenghts = [len(dataframes[0]), len(dataframes[1]), len(dataframes[2]), len(dataframes[3]), len(dataframes[4])]

    data1_mapping = {'Industry':'category',
                    'Founded':'foundationYear',
                    'Name':'name',
                    'Location':'location'}
        
    data2_mapping = {'Name': 'name',
                    'Industry': 'category',
                    'Headquarter': 'location',
                    'Foundation Year': 'foundationYear'}
        
    data3_mapping = {'name':'name',
                    'valuation': 'marketCap',
                    'country': 'location',
                    'city': 'location',
                    'industry': 'category',
                    'founded': 'foundationYear'}
        
    data4_mapping = {'name': 'name',
                    'marketcap':'marketCap',
                    'country': 'location',
                    'sharePrice':'sharePrice',
                    'categories':'category'}
        
    data5_mapping = {'Name': 'name',
                    'Marketcap':'marketCap',
                    'Share price':'sharePrice'}
    
    mapping_list = [data1_mapping, data2_mapping, data3_mapping, data4_mapping, data5_mapping]

    fm = FlexMatcher(schema_list, mapping_list, random_state, sample_size=max(lenghts))

    start = datetime.now()
    fm.train()
    end = datetime.now()
    print("Required time: " + str(end-start))

    if save is True:
        model_filepath = "./1 - Schema Matching/"
        model_filename = "flexmatcher_pt.pkl"
        with open(model_filepath+model_filename, 'wb') as f:
            pickle.dump(fm, f)

    return fm

def load_trained_flexmatcher():
    model_filepath = "./1 - Schema Matching/"
    model_filename = "flexmatcher_pt.pkl"
    fm = None
    with open(model_filepath+model_filename, 'rb') as f:
        fm = pickle.load(f)
        print("Pre-trained FlaxMatcher loaded!\n")
    
    return fm

def get_predictions(fm, folder):
    print("PREDICTIONS FOR:", folder)
    files = os.listdir(folder)

    for file in files:
        if file.endswith('csv'):
            print("File ->", file)
            schema = pd.read_csv(folder+file, dtype='object')
            print(fm.make_prediction(schema))
    
    print()


def predict_fm(schema, fm):    
    return fm.make_prediction(schema)

### #### ###
### MAIN ###
### #### ###
        
# Riaddestrare il Modello da capo ed eseguire la predizione
train_sources_folder = './datasets/train_sources/'
random_state = 24

# Preparazione del Training Set
dataframes = prepare_training_set(train_sources_folder)

# Addestramento del Modello
# Rimuovere il Commento dalla Riga seguente per riaddestrare FlexMatcher
# fm = train_flexmatcher(dataframes, random_state, save=True)

# Caricare il Modello pre-addestrato ed eseguire la predizione
fm = load_trained_flexmatcher()

# Testing
get_predictions(fm, folder="./datasets/test_sources/Addi/")
get_predictions(fm, folder="./datasets/test_sources/Alessandro/")
get_predictions(fm, folder="./datasets/test_sources/Fabio/")
get_predictions(fm, folder="./datasets/test_sources/Riccardo/")