import os
import csv
import json
import pickle
import pandas as pd
import numpy as np
from flexmatcher import FlexMatcher
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")   # LogisticRegression non converge, eliminati i warnings per alleggerire il Prompt

### ################# ###
### SUPPORT FUNCTIONS ###
### ################# ###

# Funzione per la lettura di file csv
def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8', errors='ignore') as csv_file:
        csv_reader = csv.reader(csv_file)
        return [row for row in csv_reader]

# Funzione per la lettura di file JSON
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as json_file:
        return json.load(json_file)

#Funzione per la lettura di file jsonl
def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as jsonl_file:
        json_lines = jsonl_file.readlines()
        if json_lines:
            first_json_dict = json.loads(json_lines[0])
            result = [list(first_json_dict.keys())]

            for json_line in json_lines:
                json_dict = json.loads(json_line)
                result.append(list(json_dict.values()))

            return result
        else:
            return []

#Funzione per la lettura di excel
def read_excel(file_path):
    return pd.read_excel(file_path)

#Funzione che estrae le informazioni presenti una directory
def import_values_from_folder(folder_path):
    source_dict = {}
    file_extensions = ['.csv','.json','.jsonl', '.xlsx']

    for file_name in os.listdir(folder_path):
        if any(file_name.endswith(ext) for ext in file_extensions):
            file_path = os.path.join(folder_path, file_name)
            current_file_values = read_file(file_path)
            source_dict[file_name] = current_file_values

    return source_dict

#Funzione per la lettura di file
def read_file(file_path):
    if file_path.endswith('.csv'):
        return read_csv(file_path)
    elif file_path.endswith('.json'):
        return read_json(file_path)
    elif file_path.endswith('.jsonl'):
        return read_jsonl(file_path)
    elif file_path.endswith('.xlsx'):
        return read_excel(file_path)
    else:
        # Gestisci altri tipi di file se necessario
        print(f"Tipo di file non supportato: {file_path}")
        return None

def remove_columns(data, columns_to_remove):
    """
    Remove specified columns from the DataFrame.

    Parameters:
    - data: pandas DataFrame
    - columns_to_remove: list of column names to be removed

    Returns:
    - Modified DataFrame without the specified columns
    """
    return data.drop(columns=columns_to_remove, errors='ignore')

def prepare_training_set(source_dict, with_no_map):
    # SOURCE 1
    forbes_values = source_dict.get('forbes3.csv')
    header = forbes_values.pop(0)
    data1 = pd.DataFrame(forbes_values, columns=header)
    if (with_no_map is False):
        columns_to_remove_data1 = ['Revenue']
        data1 = remove_columns(data1, columns_to_remove_data1)

    # SOURCE 2
    ambition_box_values = source_dict.get('AmbitionBox.csv')
    header = ambition_box_values.pop(0)
    data2 = pd.DataFrame(ambition_box_values, columns=header)
    if (with_no_map is False):
        columns_to_remove_data2 = ['Ownership']
        data2 = remove_columns(data2, columns_to_remove_data2)

    # SOURCE 3
    cbinsight_values = source_dict.get('DDDcbinsight.csv')
    header = cbinsight_values.pop(0)
    data3 = pd.DataFrame(cbinsight_values, columns=header)
    data3.drop([''], axis=1, inplace=True)
    if (with_no_map is False):
        columns_to_remove_data3 = ['dateJoined', 'investors', 'stage', 'totalRaised']
        data3 = remove_columns(data3, columns_to_remove_data3)

    # SOURCE 4
    companies_marketCap_values = source_dict.get('companiesMarketCap_dataset.jsonl')
    header = companies_marketCap_values.pop(0)
    data4 = pd.DataFrame(companies_marketCap_values,columns=header)
    data4 = data4.apply(lambda x: x.apply(lambda y: ' '.join(map(str, y)) if isinstance(y, list) else y))
    if (with_no_map is False):
        columns_to_remove_data4 = ['id', 'rank', 'change_1_day', 'change_1_year']
        data4 = remove_columns(data4, columns_to_remove_data4)

    # SOURCE 5
    data5 = source_dict.get('wissel.xlsx')
    if (with_no_map is False):
        columns_to_remove_data5 = ['ID', 'URL', 'Company code', 'Earnings', 'Revenue', 'Shares', 'Employees']
        data5 = remove_columns(data5, columns_to_remove_data5)

    return (data1, data2, data3, data4, data5)

def train_flexmatcher(dataframes, with_no_map, random_state, save=False):
    schema_list = [dataframes[0], dataframes[1], dataframes[2], dataframes[3], dataframes[4]]

    if with_no_map is True:
        data1_mapping = {'Industry':'category',
                         'Founded':'foundationYear',
                         'Revenue': '<NO_MAP>',
                         'Name':'name',
                         'Location':'location'}
        
        data2_mapping = {'Name':'name',
                         'Industry':'category',
                         'Headquarter': 'location',
                         'Ownership': '<NO_MAP>',
                         'Foundation Year':'foundationYear'}
        
        data3_mapping = {'name':'name',
                         'valuation':'marketCap',
                         'dateJoined': '<NO_MAP>',
                         'country': 'location',
                         'city':'location',
                         'industry':'category',
                         'investors': '<NO_MAP>',
                         'founded':'foundationYear',
                         'stage': '<NO_MAP>',
                         'totalRaised': '<NO_MAP>'}
        
        data4_mapping = {'id': '<NO_MAP>',
                         'name': 'name',
                         'rank': '<NO_MAP>',
                         'market_cap':'marketCap',
                         'country': 'location',
                         'share_price':'sharePrice',
                         'change_1_day': '<NO_MAP>',
                         'change_1_year': '<NO_MAP>',
                         'categories':'category'}
        
        data5_mapping = {'URL': '<NO_MAP>',
                         'ID': '<NO_MAP>',
                         'Name': 'name',
                         'Company code': '<NO_MAP>',
                         'Marketcap':'marketCap',
                         'Share price':'sharePrice',
                         'Earnings': '<NO_MAP>',
                         'Revenue': '<NO_MAP>',
                         'Shared': '<NO_MAP>',
                         'Employees': '<NO_MAP>'}
    
    else:
        data1_mapping = {'Founded':'foundationYear',
                         'Name':'name',
                         'Location':'location',
                         'Industry':'category'}
        
        data2_mapping = {'Name':'name',
                         'Industry':'category',
                         'Headquarter': 'location',
                         'Foundation Year':'foundationYear'}
        
        data3_mapping = {'name':'name',
                         'valuation':'marketCap',
                         'country': 'location',
                         'city':'location',
                         'industry':'category',
                         'founded':'foundationYear'}
        
        data4_mapping = {'name': 'name',
                         'market_cap':'marketCap',
                         'country': 'location',
                         'share_price':'sharePrice',
                         'categories':'category'}
        
        data5_mapping = {'Name': 'name',
                         'Marketcap':'marketCap',
                         'Share price':'sharePrice'}

    
    mapping_list = [data1_mapping, data2_mapping, data3_mapping, data4_mapping, data5_mapping]

    fm = FlexMatcher(schema_list, mapping_list, random_state, sample_size=2000)
    start = datetime.now()
    fm.train()
    end = datetime.now()
    print("Required time: " + str(end-start))

    if save is True:
        model_filepath = "./src/"
        model_filename = "flexmatcher_5_sources.pkl"
        with open(model_filepath+model_filename, 'wb') as f:
            pickle.dump(fm, f)

    return fm

def load_trained_flexmatcher():
    model_filepath = "./src/"
    model_filename = "flexmatcher_2000.pkl"
    fm = None
    with open(model_filepath+model_filename, 'rb') as f:
        fm = pickle.load(f)
        print("Pre-trained FlaxMatcher loaded!")
    
    return fm

def predict_flexmatcher(schema, fm):
    # Sul DataFrame da classificare tutte le colonne devono contenere valori di tipo 'stringa'
    for column in schema.columns:
        series = schema[column]
        if series.dtype != object:
            values = series.to_list()
            str_values = list()
            for value in values:
                str_values.append(str(value))
            schema[column] = str_values
    
    return fm.make_prediction(schema)



### #### ###
### MAIN ###
### #### ###
        
''' Riaddestrare il Modello da capo ed eseguire la predizione'''
folder_path = './datasets/train_sources/'
with_no_map = False
random_state = 24

# Caricamento dei Dataset
source_dict = import_values_from_folder(folder_path)

# Preparazione del Training Set
dataframes = prepare_training_set(source_dict, with_no_map)

# Addestramento del Modello
#fm = train_flexmatcher(dataframes, with_no_map, random_state)


''' Caricare il Modello pre-addestrato ed eseguire la predizione'''
fm = load_trained_flexmatcher()

# Testing
test_source = "./datasets/test_sources/alessandro/"
to_predict = None
for filename in os.listdir(test_source):
    if (filename.endswith('.csv')):
        file_path = os.path.join(test_source, filename)
        to_predict = pd.read_csv(file_path)
        print(to_predict)
    if (filename.endswith(".json")):
        file_path = os.path.join(test_source, filename)
        to_predict = pd.read_json(file_path)
        
    '''
    if (filename.endswith(".jsonl")):
        file_path = os.path.join(test_source, filename)
        to_predict = read_jsonl(file_path)
        df = pd.DataFrame(to_predict)
        to_predict = df
    if (filename.endswith(".xlsx")):
        to_predict = read_excel(test_source)
    '''

    predict_mapping = predict_flexmatcher(to_predict, fm)
    print(predict_mapping)
