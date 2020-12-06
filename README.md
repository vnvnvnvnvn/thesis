# Thesis

## Install dependencies

``` shell
pip3 install -r requirements.txt
```

## Data generation

``` shell
python3 verify_MISA.py <folder>

python3 read_VS.py <json_virus_folder> <json_benign_folder>
```

Generate graphs from source files (for MISA) and json files (for VirusShare)

Generate graphs with simplified blocks from graphs

Generate the full vocabulary from simplified graphs

## Labeling basic blocks

``` shell
python3 make_transformer.py <vocab_file> <number_of_bits> <number_of_sublabels>

```

Generate the random projection matrix used for LSH

## WL

``` shell
python3 calculate_wl.py <simplified_graph_folder> [database_name] [vocab_file] [transformer_file]

```
Using the random projection matrix generated from the previous step and simplified graphs from data generation step, calculate hash from WL for all files in a folder and save them to a database

## GED
