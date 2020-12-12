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

Generate the random projection matrix used for LSH

``` shell
python3 make_transformer.py -v vs_word_file -b 32 -n vs_transformer
```
Tao database 2001 files de kiem tra

``` shell
python3 verify_hash.py --folder simp_vsgraphs --database lsh_vs.pkl -n 2001 --nested --vocab vs_word_file --transformer vs_transformer.npy
```

Kiem tra precision-recall va F1 score tinh tu database tren

``` shell
python3 verify_hash.py --database lsh_vs.pkl -s 0.95 --vocab vs_word_file --transformer vs_transformer.npy
```
Muon kiem tra cac label size khac thi chay lai buoc tao transformer voi so bit muon thu, roi chi can chay lai phan kiem tra (database khong bi anh huong boi so bit)

## WL

Using the random projection matrix generated from the previous step and simplified graphs from data generation step, calculate hash from WL for all files in a folder and save them to a database

Vi du sau tao ra database cho classify, voi 10000 files
``` shell
python3 calculate_wl.py -f simplified_vsgraphs -d vs_db_32_1.pkl -n 10000 --nested -v vs_word_file -t vs_transformer.npy

```

Vi du sau tao ra database cho detect, voi 12000 files
``` shell
python3 calculate_wl.py -f simplified_vsgraphs --benign -d benign_db_32_1.pkl -n 12000 --nested -v vs_word_file -t vs_transformer.npy

```

Vi du sau in WL hash cho mot so file

``` shell
python3 calculate_wl.py --file example_simplified_MISA/dwarf_add64_1 --file example_simplified_MISA/dwarf_add_abbrev_1 -v word_file_x86 -t x86_transformer.npy
```

Neu muon chay TF-IDF can tao ra database cho phuong phap do nhu sau

``` shell
python3 label_tf_idf.py --core benign_db_32_1
```

Chay thi nghiem voi cac database da tao ra nhu sau (1000 queries nhu trong vs_experiment_1000.txt)

``` shell
python3 run_wl_experiments.py -q 1000 --core vs_db_32_1 -t classify -d iou -f classify.txt -v

```
``` shell
python3 run_wl_experiments.py -q 1000 --core vs_db_32_1_normed -t classify -d idf -f classify.txt -v

```
Ket qua se duoc viet vao file `classify.txt`. Tuong tu voi cac task khac

Huong dan visualize ket qua o phan Visualize.

## GED

Tao ra graph data GED co the dung nhu sau

``` shell
python3 test_ged.py -f simp_graphs/x86 -g ged_misa_x86 -d wl_data/misa_db_x86_32_1.pkl -v word_file_x86 -t x86_transformer
```
Kiem tra la GED co hoat dong

``` shell
python3 test_ged.py --test -f example_simplified_MISA -v word_file_x86 -t x86_transformer.npy

```

Chay task retrieval dung GED

``` shell
python3 test_ged.py -d wl_data/misa_db_x86_32_1.pkl -g ged_misa_x86 -q 5 -n 10
```

Co the doc huong dan chi tiet hon bang cach chay

``` shell
python3 test_ged.py -h
```

So sanh giua GA va non-GA

``` shell
python3 ga_ged.py --folder ged_misa_arm -n 10
```

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
