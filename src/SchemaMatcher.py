import os
import csv
import json
import pandas as pd
import flexmatcher
import numpy as np


def import_values_from_folder(folder_path):
    # Inizializza un dizionario vuoto per contenere i valori
    all_values = {}

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
        all_values[file_name] = current_file_values

    return all_values

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


# Sostituisci 'percorso_della_tua_cartella' con il percorso effettivo della tua cartella
folder_path = '/Users/alessandropesare/dataset_Progetto_Finale_IDD'

all_values = import_values_from_folder(folder_path)

# Accedi ai valori di ciascun file CSV
forbes_values = all_values.get('forbes3.csv')
ambition_box_values = all_values.get('AmbitionBox.csv')
cbinsight_values = all_values.get('DDDcbinsight.csv')
companies_marketCap_values = all_values.get('companiesMarketCap_dataset.jsonl')


# Visualizza i valori di ciascun file CSV
print("Forbes Values:", forbes_values[0])
print("Ambition Box Values:", ambition_box_values[0])
print("CB Insight Values:", cbinsight_values[0])
print("Companies MarketCap Values:", companies_marketCap_values[0])

#Da migliorare o meglio generalizzare
header = forbes_values.pop(0)
data1 = pd.DataFrame(forbes_values, columns=header)
header = ambition_box_values.pop(0)
data2 = pd.DataFrame(ambition_box_values, columns=header)
header = cbinsight_values.pop(0)
data3 = pd.DataFrame(cbinsight_values, columns=header)
header = companies_marketCap_values.pop(0)
data4 = pd.DataFrame(companies_marketCap_values,columns=header)

columns_to_remove_data1 = ['Revenue']
columns_to_remove_data2 = ['Ownership']
columns_to_remove_data3 = ['', 'dateJoined', 'investors', 'stage', 'totalRaised']
columns_to_remove_data4 = ['id', 'rank', 'change_1_day', 'change_1_year']

# Apply the remove_columns method to each dataset
data1 = remove_columns(data1, columns_to_remove_data1)
data2 = remove_columns(data2, columns_to_remove_data2)
data3 = remove_columns(data3, columns_to_remove_data3)
data4 = remove_columns(data4, columns_to_remove_data4)


#defizione mapping per addestramento
data1_mapping = {
                 'Founded':'foundationYear',
                 'Name':'name',
                 'Location':'location',
                 'Industry':'category'
                }
data2_mapping = {'Name':'name',
                 'Industry':'category',
                 'Headquarter': 'location',
                 'Foundation Year':'foundationYear'
                }
#dubbio attributi mappati nello stesso attributo sovrascivono i valori?
data3_mapping = {
                 'name':'name',
                 'valuation':'marketCap',
                 'country': 'location',
                 'city':'location',
                 'industry':'category',
                 'founded':'foundationYear',

                }
data4_mapping = {'name': 'name',
                 'market_cap':'marketCap',
                 'country': 'location',
                 'share_price':'sharePrice',
                 'categories':'category'}

data4 = data4.apply(lambda x: x.apply(lambda y: ' '.join(map(str, y)) if isinstance(y, list) else y))

schema_list = [data1,data2,data3,data4]
print(schema_list)

mapping_list = [data1_mapping,data2_mapping,data3_mapping,data4_mapping]
print(mapping_list)
fm = flexmatcher.FlexMatcher(schema_list, mapping_list)

fm.train()

# creating the test dataset

vals3 = [['Nome','Località','Settore'],
        ['AppleInc.','United States','Technology'],
        ['Arabian Oil Company', 'Saudi Arabia','Energy'],
        ['Fiat','Italy','Motors'],
        ['Huawei','China','Technology']]

header = vals3.pop(0)
data3 = pd.DataFrame(vals3, columns=header)
#print(data3)

predicted_mapping = fm.make_prediction(data3)

# Visualizza i risultati finali
print(predicted_mapping)
#print(predicted_mapping['Nome'])
#print(predicted_mapping['Località'])
#print(predicted_mapping['Settore'])
