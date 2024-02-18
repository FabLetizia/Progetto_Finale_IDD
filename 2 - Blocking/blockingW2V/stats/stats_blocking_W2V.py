import pandas as pd

### #################### ###
### FUNZIONI DI SUPPORTO ###
### #################### ###

def create_dimension2block(report_filepath):
    dimension2block = dict()

    cluster_report = pd.read_csv(report_filepath)
    for i in range(0, len(cluster_report)):
        row = cluster_report.iloc[i]
        block_idx = int(row['block'])

        if block_idx not in dimension2block:
            dimension2block[block_idx] = 1
        else:
            dimension2block[block_idx] = dimension2block.get(block_idx) + 1
        
    block_ids = list(dimension2block.keys())
    dimensions = list(dimension2block.values())
    
    df = pd.DataFrame(columns=['Block_ID', 'Number of Records'])
    df['Block_ID'] = block_ids
    df['Number of Records'] = dimensions
    df.to_csv("./2 - Blocking/blockingW2V/dimension2block_W2V.csv", index=False)

def create_frequency2dimension(d2b_filepath):
    frequency2dimension = dict()
    dimension2block = pd.read_csv(d2b_filepath)

    for i in range(0, len(dimension2block)):
        row = dimension2block.iloc[i]
        dimension = row['Number of Records']

        if dimension not in frequency2dimension:
            frequency2dimension[dimension] = 1
        else:
            frequency2dimension[dimension] = frequency2dimension.get(dimension) + 1
    
    frequency2dimension_ordered = dict(sorted(frequency2dimension.items(), key=lambda x: x[0]))
    dimensions = list(frequency2dimension_ordered.keys())
    num_blocks = list(frequency2dimension_ordered.values())

    df = pd.DataFrame(columns=['Dimension', 'Number of Blocks'])
    df['Dimension'] = dimensions
    df['Number of Blocks'] = num_blocks
    df.to_csv("./2 - Blocking/blockingW2V/frequency2dimension_W2V.csv", index=False)

### #### ###
### MAIN ###
### #### ###

report_filepath = "./2 - Blocking/blockingW2V/stats/SchemaMediatoConCluster.csv"
d2b_filepath = "./2 - Blocking/blockingW2V/dimension2block_W2V.csv"

create_dimension2block(report_filepath)
create_frequency2dimension(d2b_filepath)