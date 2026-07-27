# E-Commerce Competitive Intelligence Data Pipeline (Mini Project)

Mini project ini dibuat sebagai latihan memahami alur dasar ETL (Extract, Transform, Load) menggunakan Python, Playwright, dan PostgreSQL.

Fokus utama bukan pada skalabilitas, tetapi pada memahami bagaimana data diambil dari web dinamis, dibersihkan, lalu disimpan ke database.

## Tujuan

* Belajar scraping web dinamis menggunakan Playwright
* Memahami proses cleaning data sederhana
* Mengimplementasikan insert/update data ke PostgreSQL

## Cara Kerja

### 1. Extraction

Menggunakan Playwright (headless) untuk mengambil data dari halaman produk.

Yang dipelajari:

* Mengambil elemen dari DOM
* Menunggu elemen muncul (karena halaman dinamis)
* Menghindari loading resource tidak penting (image, dll) supaya lebih cepat

Data yang diambil:

* SKU
* Nama produk
* Harga (masih string)
* Status stok
* Rating

### 2. Transformation

Data dibersihkan sebelum disimpan:

* Harga:

  * Dari string → angka (pakai regex sederhana)
* Stok:

  * Teks → boolean
* Timestamp:

  * Ditambahkan untuk menandai waktu pengambilan data

Masih banyak edge case yang belum ditangani (format harga berbeda-beda, dll).

### 3. Loading

Data dimasukkan ke PostgreSQL menggunakan psycopg2.

Menggunakan konsep UPSERT:

* Jika SKU belum ada → insert
* Jika sudah ada → update

Ini dipakai supaya data tidak duplikat.

### 4. Validasi Sederhana

Menggunakan query dasar:

* Total jumlah produk
* Rata-rata harga

## Keterbatasan

* Scraping masih rentan jika struktur website berubah
* Error handling masih minim
* Belum ada automation (belum pakai cron/scheduler)
* Belum ada logging

## Catatan

Project ini masih tahap belajar, jadi fokus pada pemahaman konsep dasar ETL, bukan production-ready system.
