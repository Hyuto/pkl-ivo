# Script PKL Ivosight

Script buat automatisasi tugas - tugas PKL di Ivosight

**Clone repo ini**

```bash
git clone https://github.com/Hyuto/pkl-ivo.git
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
