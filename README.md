README Aplikasi Optimasi Penjadwalan FSP-ABC
===========================================

1. Instalasi Python dan Virtual Environment
------------------------------------------

Pastikan Python 3.10 atau lebih tinggi telah terpasang.
Kemudian jalankan perintah berikut di folder proyek:

    python -m venv venv
    source venv/bin/activate

Setelah environment aktif, install dependensi:

    pip install -r requirements.txt

Jika file requirements.txt tidak tersedia, install paket berikut:

    pip install streamlit pandas numpy plotly

2. Struktur Utama Proyek
------------------------

- app.py            : aplikasi Streamlit utama
- logic/abc_algorithm.py : implementasi algoritma ABC untuk Flow Shop
- utils/utils.py    : fungsi validasi, perhitungan jadwal, dan pembuatan gantt chart
- data/             : contoh dataset bawaan dan dataset tambahan

3. Menjalankan Aplikasi
-----------------------

Jalankan aplikasi dengan perintah:

    streamlit run app.py

Buka alamat yang ditampilkan di browser (biasanya http://localhost:8501).

4. Penggunaan Aplikasi
----------------------

Tab 1: Optimasi Utama

- Pilih dataset bawaan atau unggah file CSV Anda sendiri.
- Isi parameter:
  - Colony Size
  - Maksimum Iterasi
  - Limit Trial
  - Number of Sequence (NSE)
  - Jumlah Percobaan (untuk tabel uji)
- Klik tombol "Jalankan Optimasi".

Hasil yang muncul:
- Waktu pengerjaan total (makespan)
- Nilai fitness terbaik
- Urutan job terbaik
- Gantt chart jadwal pengerjaan
- Tabel hasil percobaan dengan nilai fitness dan makespan setiap kali run
- Grafik fitness per percobaan

Catatan: "Jumlah Percobaan" tidak mengubah parameter algoritma ABC itu sendiri.
Ia menentukan berapa kali algoritma dijalankan ulang untuk mencari solusi terbaik secara stokastik.

Tab 2: Pengujian Parameter (Analisis)

Tab ini digunakan untuk melakukan eksperimen parameter dan mencari nilai terbaik untuk:
- Limit Trial
- Jumlah Iterasi

Fungsi ini berguna untuk menentukan pengaturan parameter yang optimal sebelum menggunakan tab utama.

Langkah penggunaannya:
- Pilih jenis pengujian: iterasi atau limit.
- Tentukan daftar nilai yang ingin diuji.
- Tentukan parameter tetap lainnya.
- Klik "Jalankan Pengujian".

Hasil yang muncul:
- Tabel hasil setiap nilai parameter
- Rata-rata fitness per nilai parameter
- Grafik perbandingan hasil uji coba

5. Tips Praktis
---------------

- Gunakan dataset bawaan untuk memastikan aplikasi bekerja terlebih dahulu.
- Untuk dataset eksternal, pastikan kolom pertama berisi label job (misalnya J1, J2, ...)
  dan kolom berikutnya berisi durasi tahap seperti M1, M2, M3, ...
- Aplikasi akan menormalisasi label job dan kolom tahap secara otomatis.
- Jika ingin stabilitas hasil, jalankan beberapa percobaan dengan "Jumlah Percobaan" lebih besar.

6. Contoh Perintah Mesin
-------------------------

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py
7. Value yang disarankan untuk Pengujian Parameter (Analisis)
-------------------------

- Pada pengujian Batas parameter Iterasi gunakan setidaknya 5 nilai percobaan, Meskipun pada jurnal refrensi
kami menjelaskan bawwa Percobaan per nilai adalah 3, namun hasil tiap run program kurang stabil untuk 
mendapatkan hasil iterasi 60 sebagai nilai fitness terbaik
- Pada pengujian Batas Parameter limit juga disarankan di 5 nilai percobaan untuk menghasilkan nilai stabil yang 
yaitu 5 parameter Limit
- Refrensi Github untuk dataset diluar gumcode sebagai berikut https://github.com/akilelkamel/fssp-dataset


Semoga membantu! Jika ingin dokumentasi tambahan atau contoh dataset, saya bisa bantu tambahkan juga.