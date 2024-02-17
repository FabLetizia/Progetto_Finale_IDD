import pandas as pd
import numpy as np
import torch
from transformers import DistilBertTokenizer, DistilBertModel
from torch import cuda
from datetime import datetime

### #################### ###
### FUNZIONI DI SUPPORTO ###
### #################### ###

def extract_features(strings):
    inputs = tokenizer(strings, return_tensors="pt", padding=True, truncation=True).to(device)
    # return_tensors="pt": ritorna tensori PyTorch
    # padding=True: frasi di lunghezza inferiore alla massima vengono adattate ad essa mediante del Padding

    with torch.no_grad():
        outputs = model(**inputs)
    last_hidden_states = outputs.last_hidden_state
    
    # Rappresentazione media e unidimensionale delle caratteristiche estratte
    features = torch.mean(last_hidden_states, dim=1).squeeze()
    to_return = features.cpu().numpy()
    
    del features
    del outputs
    del inputs
    cuda.empty_cache()

    return pd.DataFrame(to_return)

def vectorize_records(records):
    print("Inizio della Feature Extraction con DistilBERT...")
    records_vectorized = list()

    start = datetime.now()
    for i in range(0, len(records)):
        series = records.iloc[i].dropna()
        string_list = series.tolist()

        vector = np.zeros((768,))
        vector = vector.reshape(-1, 768)

        if string_list != []:
            extraction = extract_features(string_list)

            for j in range(0, len(extraction)):
                v = extraction.iloc[j].to_numpy()
                vector += v
            vector /= 768
        
        records_vectorized.append(vector)

        if i % 10000 == 0 and i != 0:
            print("Processato il Record:", i)
    end = datetime.now()

    print("Fine della Feature Extraction! Required Time:", str(end-start))

    vectors_df = pd.DataFrame(np.concatenate(records_vectorized, axis=0))
    return vectors_df

### #### ###
### MAIN ###
### #### ###

records = pd.read_csv("./datasets/MediatedSchemaSemicolon.csv", sep=';')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

device = None
availability = cuda.is_available()
if availability:
    print("Device per la Feature Extraction con DistilBERT ->", cuda.get_device_name())
    device = 'cuda'
else:
    print("Device per la Feature Extraction con DistilBERT -> CPU")
    device = 'cpu'

model.to(device)

vectors_df = vectorize_records(records)
vectors_df.to_csv("./datasets/fileprova.csv", index=False)