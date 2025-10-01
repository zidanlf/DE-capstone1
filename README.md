# DE-capstone1

**Capstone Project - Data Engineering**  
Oleh: [zidanlf](https://github.com/zidanlf)

---

## 🚀 Deskripsi Singkat

Proyek ini adalah implementasi pipeline ETL (Extract, Transform, Load) untuk dua domain data nyata:  
1. **Produk E-Commerce** (analisis harga, diskon, revenue potensial, dsb.)  
2. **Lowongan Kerja/Recruitment** (analisis gaji, parsing skills, tipe kerja, dsb.)

Pipeline modular ini mengotomatisasi pembersihan data, ekstraksi insight, serta menyimpan hasilnya dalam format Excel multi-sheet & file profiling .txt. Cocok untuk studi kasus, pembelajaran, hingga pondasi sistem data pipeline production.

---

## 📁 Struktur Direktori

```
DE-capstone1/
├── config/
│   └── config.py                # Path konfigurasi file data
├── data_products/               # Pipeline ETL untuk data produk
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── data_profiling.py
├── data_recruitment/            # Pipeline ETL untuk data recruitment
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── data_profiling.py
├── output/                      # Hasil Excel & TXT profiling
├── main_products.py             # Main runner produk e-commerce
├── main_recruitment.py          # Main runner recruitment
├── requirements.txt             # Daftar dependensi Python
└── README.md
```

---

## 🛠️ Fitur Utama

- **Extract:** Baca raw data CSV secara dinamis.
- **Transform:** 
  - Data cleaning, parsing, dan normalisasi (handling null, typecast, regex, dsb.)
  - Feature engineering (potensi revenue/loss, parsing skill, deteksi job type, dsb.)
  - Analisis statistik & bisnis (ringkasan, distribusi, top-N, dsb.)
- **Profiling:** Output otomatis ringkasan info, missing value, duplicate, statistik, dsb. ke txt.
- **Load:** Simpan data hasil ETL dan analisis ke file Excel multi-sheet.
- **Modular, reusable:** Struktur folder dan fungsi mudah dikembangkan.
- **Configurable:** Path dan parameter bisa disesuaikan lewat file config.
- **Error handling:** Robust terhadap missing data, format anomali, dsb.
- **Analisis Bisnis Otomatis:** Insight bisnis (misal: produk diskon tertinggi, rata-rata salary, dsb.) langsung diproses.

---

## 📦 Instalasi & Requirement

### 1. Clone Repository

```bash
git clone https://github.com/zidanlf/DE-capstone1.git
cd DE-capstone1
```

### 2. (Direkomendasikan) Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/Mac
venv\Scripts\activate     # Untuk Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Path Data

Edit file `config/config.py` agar sesuai lokasi file data Anda:

```python
PATH_FILE_PRODUCTS = "data/raw/products.csv"
PATH_FILE_RECRUITMENT = "data/raw/recruitments.csv"
```
Pastikan file CSV tersedia di path tersebut.

---

## ▶️ Cara Menjalankan Pipeline

### Pipeline Produk E-Commerce

```bash
python main_products.py
```

### Pipeline Data Recruitment

```bash
python main_recruitment.py
```

- Output akan otomatis tersimpan di folder `output/` berupa file Excel (.xlsx) dan file profiling (.txt).

---

## 📊 Penjelasan Fungsional Script

### Main Runner
- **main_products.py**  
  Pipeline ETL untuk data produk e-commerce.
- **main_recruitment.py**  
  Pipeline ETL untuk data lowongan kerja.

### ETL Modul

#### data_products/
- **extract.py**  
  Fungsi membaca CSV produk.
- **transform.py**  
  - Cleaning kolom harga, diskon, parsing currency, handle null/format anomali.
  - Hitung revenue potensial, potensi kerugian diskon, dsb.
  - Analisis statistik (mean, median, distribusi harga, top revenue, dsb.)
- **load.py**  
  Simpan hasil ETL & analisis ke Excel multi-sheet.
- **data_profiling.py**  
  Simpan ringkasan info, describe, missing value, duplicate, dsb. ke txt.

#### data_recruitment/
- **extract.py**  
  Fungsi membaca CSV recruitment.
- **transform.py**  
  - Cleaning kolom (company, rating, dsb), parsing deskripsi kerja (skills, level, jenis kerja, benefit).
  - Parsing salary (float+unit+currency), imputasi salary, normalisasi tipe data.
  - Analisis statistik (top skills, distribusi experience, distribusi salary, top company, dsb).
- **load.py**  
  Simpan hasil ETL & analisis ke Excel multi-sheet.
- **data_profiling.py**  
  Output ringkasan profiling ke txt.

---

## 📝 Contoh Output

- `output/All Exercise and Fitness.xlsx` — hasil ETL data produk, dengan banyak sheet analitik.
- `output/inspect_data_product.txt` — ringkasan profiling produk.
- `output/data_requirements.xlsx` — hasil ETL data recruitment.
- `output/inspect_data_recruitment.txt` — ringkasan profiling recruitment.

---

## 🧑‍💻 Dokumentasi Fungsi Utama

### Data Produk

| Fungsi | File | Deskripsi Singkat |
|--------|------|------------------|
| `extract_product` | data_products/extract.py | Membaca file CSV produk |
| `transform_product` | data_products/transform.py | Membersihkan, parsing, dan analisis data produk |
| `demographi` | data_products/transform.py | Membuat laporan statistik & bisnis produk |
| `load_product` | data_products/load.py | Simpan data dan report multi-sheet ke Excel |
| `inspect_data` | data_products/data_profiling.py | Profiling data ke TXT |

### Data Recruitment

| Fungsi | File | Deskripsi Singkat |
|--------|------|------------------|
| `extract_recruitment` | data_recruitment/extract.py | Membaca CSV recruitment |
| `transform` | data_recruitment/transform.py | Cleaning, parsing deskripsi, salary, dsb. |
| `demographi` | data_recruitment/transform.py | Statistik & insight bisnis/teknis recruitment |
| `load` | data_recruitment/load.py | Simpan hasil ke Excel multi-sheet |
| `inspect_data` | data_recruitment/data_profiling.py | Profiling TXT |

---

## 📚 Penjelasan Transformasi & Analisis

### Produk
- **Cleaning harga/diskon:** Parsing currency & nominal, handle string anomali ("GET", "FREE Delivery").
- **Feature engineering:**  
  - `discount_percentage`, `potential_revenue`, `potential_loss_from_discount`
- **Analisis bisnis:**  
  - Produk dengan diskon tertinggi, revenue terbesar, distribusi harga.

### Recruitment
- **Parsing deskripsi:** Deteksi skills populer, experience level, tipe kerja (full-time, remote, dsb.), benefit kerja.
- **Salary Parsing:** Ekstraksi angka, unit (per year/hour), currency.
- **Imputasi salary:** Isi salary kosong dari job serupa.
- **Analisis:** Distribusi skill, pengalaman, job type, salary, company posting terbanyak.
