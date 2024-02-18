import pandas as pd

### #################### ###
### FUNZIONI DI SUPPORTO ###
### #################### ###

def create_dimension2block(report_filepath):
    dimension2block = dict()

    with open(report_filepath, 'r') as file:
        for line in file:
            record, block_idx = line.strip().split(':')
            record = int(record)
            block_idx = int(block_idx)

            if block_idx not in dimension2block:
                dimension2block[block_idx] = 1
            else:
                dimension2block[block_idx] = dimension2block.get(block_idx) + 1
    
    block_ids = list(dimension2block.keys())
    dimensions = list(dimension2block.values())

    df = pd.DataFrame(columns=['Block_ID', 'Number of Records'])
    df['Block_ID'] = block_ids
    df['Number of Records'] = dimensions
    df.to_csv("./2 - Blocking/blockingRulesGPT/dimension2block_GPT.csv", index=False)

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
    df.to_csv("./2 - Blocking/blockingRulesGPT/frequency2dimension_GPT.csv", index=False)

### #### ###
### MAIN ###
### #### ###

report_filepath = "./2 - Blocking/blockingRulesGPT/clustering_full_24.txt"
d2b_filepath = "./2 - Blocking/blockingRulesGPT/dimension2block_GPT.csv"

create_dimension2block(report_filepath)
create_frequency2dimension(d2b_filepath)