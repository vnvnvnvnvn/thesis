# Thesis

## Install dependencies

``` shell
pip3 install -r requirements.txt
```

## Data generation

### MISA
Chuyen cac file trong folder MISA x86 ra dang don gian, viet ket qua vao simp_graphs/x86, tao file vocab word_file_x86
``` shell
python3 verify_MISA.py -a -f MISA/source/x86 --arch x86 --vocab --simplified_folder simp_graphs/x86 --graphs_folder graphs/x86
```

Chuyen file `binutils-2.30-O1-dwarf.c.s` thanh dang don gian, luu vao example_simplified_MISA, ve cac graph da tao duoc
``` shell
python3 verify_MISA.py --file binutils-2.30-O1-dwarf.c.s --arch x86 -v
```
De in (hoac ve) 5 graphs trong so se tao ra
``` shell
python3 verify_MISA.py --file binutils-2.30-O1-dwarf.c.s --arch x86 -v -i -n 5
```


### VS

Chuyen toan bo virus binary sang json

``` shell
python3 make_json.py RAW_final_dataset
```
Chuyen toan bo danh sach benign binary sang json

``` shell
python3 make_json.py exe.txt
```

Xu ly toan bo folder VS
``` shell
python3 read_VS.py -a -f virus_jsons -b benign_jsons
```
Generate full vocabulary from simplified graphs

``` shell
python3 read_VS.py -a --vocab
```

Chuyen 1 binary sang json

``` shell
python3 make_json.py /bin/ls
```
Xu ly mot binary

``` shell
python3 read_VS.py --file ls.json
```

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
### Graph

``` shell
./visualize_graph.py example_simplified_MISA/elflink__bfd_elf_merge_sections_1
```

### Word TF-IDF

Se ve vao hai files _wc va _idf tuong ung (MISA)

``` shell
./tf_idf.py --folder simp_graphs/x86 --vocab word_file_x86

```

VS (can nested folder)

``` shell
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
