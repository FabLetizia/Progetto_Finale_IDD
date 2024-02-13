import pandas as pd

### ******************** ###
### FUNZIONI DI SUPPORTO ###
### ******************** ###
def column_values_to_string(column):
    new_col = list()
    for val in column:
        new_col.append(str(val))
    return new_col

def string_list_to_string(column):
    new_col = list()
    for string in column:
        string = string.replace('\'', '')
        string = string.replace('[', '')
        string = string.replace(']', '')
        new_col.append(string)
    return new_col

### ****************** ###
### FUNZIONI OPERATIVE ###
### ****************** ###
def preprocess_sources():
    train_folder = "./datasets/train_sources/"
    addi_folder = "./datasets/test_sources/Addi/"
    alessandro_folder = "./datasets/test_sources/Alessandro/"
    fabio_folder = "./datasets/test_sources/Fabio/"
    riccardo_folder = "./datasets/test_sources/Riccardo/"
    files = [
        str(train_folder + "DDD-cbinsight.csv"),
        str(train_folder + "FR-forbes.csv"),
        str(train_folder + "iGMM-companiesMarketCap.csv"),
        str(train_folder + "MarScoToc-AmbitionBox.csv"),
        str(train_folder + "wissel-companiesMarketCap.csv"),
        str(addi_folder + "FR-ft.csv"),
        str(addi_folder + "GioPonSpiz-companiesMarketCap.csv"),
        str(addi_folder + "MalPatSaj-disfold.csv"),
        str(addi_folder + "MarScoToc-wikipedia.csv"),
        str(alessandro_folder + "DeBiGa-globaldata.csv"),
        str(alessandro_folder + "slytherin-valueToday.csv"),
        str(alessandro_folder + "MalPatSaj-forbes.csv"),
        str(fabio_folder + "FR-sole24ore.csv"),
        str(fabio_folder + "silvestri-forbes.csv"),
        str(fabio_folder + "silvestri-disfold.csv"),
        str(fabio_folder + "silvestri-valueToday.csv"),
        str(riccardo_folder + "avengers-hitHorizons.csv"),
        str(riccardo_folder + "gren-companiesMarketCap.csv"),
        str(riccardo_folder + "slytherin-disfold.csv"),
        str(riccardo_folder + "silvestri-ft.csv")
    ]

    for file in files:
        df = pd.read_csv(file)
        columns = list(df.columns)
        for c in columns:
            col = df[c].to_list()
            first = str(col[0])
            if "[" in first and "]" in first:
                new_col = string_list_to_string(col)
            else:
                new_col = column_values_to_string(col)
            
            df[c] = new_col

        print("Preprocessing of '" + file + "' completed!")
        df.to_csv(file, index=False)
    
    print("End of Preprocessing!")


### **** ###
### MAIN ###
### **** ###
preprocess_sources()

