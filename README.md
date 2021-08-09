# Script PKL Ivosight

Script buat automatisasi tugas - tugas PKL di Ivosight

**Clone repo ini**

```bash
git clone https://github.com/Hyuto/pkl-ivo.git
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

## Emotion & OCEAN Analysis

Script : `emotion-ocean.py`

**Cara Penggunaan**

1. Single Data<br>
   Digunakan ketika data yang akan dianalisis hanya ada 1 data `csv`

   ```bash
   python emotion-ocean.py -p [PATH-KE-DATA-CSV] -a [ANALISIS]
   ```

   **Contoh** : OCEAN Analisis

   ```bash
   python emotion-ocean.py -p ./data.csv -a ocean
   ```
2. Multiple Data<br>
   Digunakan ketika data yang akan dianalisis berjumlah lebih dari 1 data `csv`

   **Penggunaan** 

   Kumpulkan data `csv` kedalam 1 folder yang sama lalu jalankan script dengan
   ketentuan berikut

   ```bash
   python emotion-ocean.py -p [PATH-KE-FOLDER] -a [ANALISIS]
   ```

   **Contoh** : OCEAN Analisis

   ```bash
   python emotion-ocean.py -p ./data -a ocean
   ```

**Exporting**

Export hasil ke `csv`? tambahkan argumen `--export` aja

Contoh: Emotion Analisis [Export]

```bash
python emotion-ocean.py -p ./data -a emotion --export
```

File `csv` akan di export kedalam folder *output*

## Forecasting

Script : `forecast.py`

**Cara Penggunaan**

1. Generate `forecasting-dataset`<br>
   Generate dataset untuk forecasting

   ```bash
   python forecast.py -p [PATH-KE-DATA | PATH-KE-FOLDER] --generate
   ```

   Contoh:

   ```bash
   python forecast -p ./data --generate
   ```

   Data nantinya akan tersimpan di folder `output`
2. Forecast<br>
   Melakukan forecasting terhadap data yang sudah di `generate` sebelumnya

   ```bash
   python forecast.py -p [PATH-KE-FORECAST-DATA] -a
   ```

   Contoh:

   ```bash
   python forecast.py -p './output/Forecast Data_01 Jan 2021 - 31 Jan 2021.csv' -a
   ```

**Exporting Performance to `csv`**

Gunakan `--export` sebagai tambahan argumen `-a` untuk mengeksport detail performance model menjadi
`csv`

Contoh :

```
python forecast.py -p './output/Forecast Data_01 Jan 2021 - 31 Jan 2021.csv' -a --export
```

## Prophet [Hanya untuk Linux]

Forecast menggunakan `Prophet`.

Supported OS: **Linux**

**Installation**

```bash
pip install pystan==2.19.1.1
pip install prophet
```

**Running Script**

```
python forecast.py -p [PATH-KE-FORECAST-DATA] -a --prophet
```

## Magic `config.json`

Atur segalanya pada file `config.json`

**Tune AutoArima**

Dokumentasi: [pmdarima.arima.AutoARIMA](https://alkaline-ml.com/pmdarima/modules/generated/pmdarima.arima.AutoARIMA.html#pmdarima.arima.AutoARIMA)
