import os
import csv
import json
import pandas as pd
import numpy as np
from flexmatcher import FlexMatcher
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")   # LogisticRegression non converge, eliminati i warnings per alleggerire il Prompt

### ################# ###
### SUPPORT FUNCTIONS ###
### ################# ###

def import_values_from_folder(folder_path):
    # Inizializza un dizionario vuoto per contenere i valori
    source_dict = {}

    # Ottieni la lista dei file nella cartella
    file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv') or f.endswith('.jsonl')]

    # Itera sui file nella cartella
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)

        # Inizializza una lista vuota per i valori del file corrente
        current_file_values = []

        # Apri il file CSV e leggi i valori
        if file_name.endswith('.csv'):
            with open(file_path, 'r', newline='', encoding='utf-8', errors='ignore') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    current_file_values.append(row)
        if file_name.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as jsonl_file:
                json_lines = jsonl_file.readlines()
                # Se ci sono righe nel file JSONL
                if json_lines:
                    # Estrai le chiavi dalla prima riga
                    first_json_dict = json.loads(json_lines[0])
                    current_file_values.append(list(first_json_dict.keys()))

                    # Itera su ogni riga successiva del file JSONL
                    for json_line in json_lines:
                        #non skippiamo la prima riga perché con get perderemmo i nomi degli attributi
                        json_dict = json.loads(json_line)
                        # Estrai i valori e concatena alla lista
                        current_file_values.append(list(json_dict.values()))

        # Assegna i valori al dizionario con il nome del file come chiave
        source_dict[file_name] = current_file_values

    return source_dict

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

    return (data1, data2, data3, data4)

def train_flexmatcher(dataframes, with_no_map, random_state):
    schema_list = [dataframes[0], dataframes[1], dataframes[2], dataframes[3]]

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
    
    mapping_list = [data1_mapping, data2_mapping, data3_mapping, data4_mapping]

    fm = FlexMatcher(schema_list, mapping_list, random_state, sample_size=2000)
    start = datetime.now()
    fm.train()
    end = datetime.now()
    print("Required time: " + str(end-start))

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
        
# Sostituisci 'percorso_della_tua_cartella' con il percorso effettivo della tua cartella
folder_path = './datasets/train_sources/'
with_no_map = True
random_state = 24

# Caricamento dei Dataset
source_dict = import_values_from_folder(folder_path)

# Preparazione del Training Set
dataframes = prepare_training_set(source_dict, with_no_map)

# Addestramento del Modello
fm = train_flexmatcher(dataframes, with_no_map, random_state)

# Testing del Modello
test_source = "./datasets/test_sources/silvestri-ft.com.csv"
to_predict = None
if (test_source.endswith('.csv')):
    to_predict = pd.read_csv(test_source)

predict_mapping = predict_flexmatcher(to_predict, fm)
print(predict_mapping)