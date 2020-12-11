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

## Visualize
### Word TF-IDF

Se ve vao hai files _wc va _idf tuong ung

``` shell
./tf_idf.py --folder simp_graphs/x86 --vocab word_file_x86
./tf_idf.py --folder simp_vs_graphs/ --nested --vocab vs_word_file
```

### LSH data
In bang F1 cua LSH data da thu duoc

``` shell
./plot_lsh.py --f1
```

Ve hai duong LSH trong cung mot hinh. Ket qua duoc ve o hinh lsh_plot.png (co the thay doi bang option `--save_fig`)

``` shell
./plot_lsh --line vs_data --line vs_data_95
```


### Detect data

In precision, recall va F1 cho ket qua detect
``` shell
./plot_confusion.py --file detect.txt --task detect
```

### Classify data

Ve hinh confusion matrix cho ket qua phan loai
``` shell
./plot_confusion.py --file vs_experiment_1000.txt --task classify
```
