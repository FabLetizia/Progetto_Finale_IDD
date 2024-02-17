import os
import csv
import json
import pandas as pd

### ******************** ###
### FUNZIONI DI SUPPORTO ###
### ******************** ###
def read_file(file_path):
    if file_path.endswith('.csv'):
        return read_csv(file_path)
    elif file_path.endswith('.json'):
        return read_json(file_path)
    elif file_path.endswith('.jsonl'):
        return read_jsonl(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return read_excel(file_path)
    else:
        # Gestisci altri tipi di file se necessario
        print(f"Tipo di file non supportato: {file_path}")
        return None

def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8', errors='ignore') as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = [row for row in csv_reader]
        columns = rows.pop(0)
        return pd.DataFrame(rows, columns=columns)

def read_json(file_path):
    return pd.read_json(file_path)

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as jsonl_file:
        json_lines = jsonl_file.readlines()
        if json_lines:
            first_json_dict = json.loads(json_lines[0])
            result = [list(first_json_dict.keys())]

            for json_line in json_lines:
                json_dict = json.loads(json_line)
                result.append(list(json_dict.values()))
        else:
            result = list()
    
    columns = result.pop(0)
    return pd.DataFrame(result, columns=columns)

def read_excel(file_path):
    return pd.read_excel(file_path)

### ****************** ###
### FUNZIONI OPERATIVE ###
### ****************** ###
def train_sources_to_csv():
    train_sources_folder = "./datasets/train_sources/"
    file_paths = [
        str(train_sources_folder + "DDD-cbinsight.csv"),
        str(train_sources_folder + "MarScoToc-AmbitionBox.csv"),
        str(train_sources_folder + "FR-forbes.csv"),
        str(train_sources_folder + "wissel-companiesMarketCap.csv"),
        str(train_sources_folder + "iGMM-companiesMarketCap.json")
    ]

    for file in file_paths:
        dest_path = file
        df = read_file(file)

        if file.endswith('.jsonl'):
            dest_path = file[0:-6] + '.csv'
        if file.endswith('.json') or file.endswith('.xlsx'):
            dest_path = file[0:-5] + '.csv'
        if file.endswith('.xls'):
            dest_path = file[0:-4] + '.csv'

        df.to_csv(dest_path, index=False)
        print("File '" + file + "' convertito con successo!")

def test_sources_to_csv():
    addi_sources_folder = "./datasets/test_sources/Addi/"
    alessandro_sources_folder = "./datasets/test_sources/Alessandro/"
    fabio_sources_folder = "./datasets/test_sources/Fabio/"
    riccardo_sources_folder = "./datasets/test_sources/Riccardo/"

    file_paths = [
        str(addi_sources_folder + "FR-ft.csv"),
        str(addi_sources_folder + "GioPonSpiz-companiesMarketCap.json"),
        str(addi_sources_folder + "MalPatSaj-disfold.xlsx"),
        str(addi_sources_folder + "MarScoToc-wikipedia.csv"),
        str(alessandro_sources_folder + "DeBiGa-globaldata.json"),
        str(alessandro_sources_folder + "MalPatSaj-forbes.xls"),
        str(alessandro_sources_folder + "slytherin-valueToday.json"),
        str(fabio_sources_folder + "FR-sole24ore.csv"),
        str(fabio_sources_folder + "silvestri-disfold.csv"),
        str(fabio_sources_folder + "silvestri-forbes.csv"),
        str(fabio_sources_folder + "silvestri-valueToday.csv"),
        str(riccardo_sources_folder + "avengers-hitHorizons.jsonl"),
        str(riccardo_sources_folder + "gren-companiesMarketCap.json"),
        str(riccardo_sources_folder + "slytherin-disfold.json"),
        str(riccardo_sources_folder + "silvestri-ft.csv")
    ]

    for file in file_paths:
        dest_path = file
        df = read_file(file)

        if file.endswith('.jsonl'):
            dest_path = file[0:-6] + '.csv'
        if file.endswith('.json') or file.endswith('.xlsx'):
            dest_path = file[0:-5] + '.csv'
        if file.endswith('.xls'):
            dest_path = file[0:-4] + '.csv'

        df.to_csv(dest_path, index=False)
        print("File '" + file + "' convertito con successo!")
    

### MAIN ###
train_sources_to_csv()
test_sources_to_csv()