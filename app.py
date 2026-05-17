import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from logic.abc_algorithm import run_abc
from utils.utils import (
    validate_and_preprocess, 
    calculate_timetable, 
    generate_gantt_chart, 
    convert_df_to_csv
)

st.set_page_config(page_title="Optimasi FSP-ABC", layout="wide")
st.title("Optimasi Penjadwalan Software House (FSP-ABC)")

# -- Inisialisasi Session State --
if 'df_projek' not in st.session_state:
    st.session_state.df_projek = None
if 'hasil_optimasi' not in st.session_state:
    st.session_state.hasil_optimasi = None

# Bagian Atas: Unggah Dataset (Berlaku untuk semua tab)
st.header("Dataset Projek")
use_default = st.checkbox("Gunakan Dataset Bawaan (GUMCODE)", value=True)

raw_df = None
if use_default:
    try:
        raw_df = pd.read_csv('data/dataset_gumcode.csv')
    except FileNotFoundError:
        st.error("File dataset_gumcode.csv tidak ditemukan.")
else:
    uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)

if raw_df is not None:
    is_valid, msg, clean_df = validate_and_preprocess(raw_df)
    if is_valid:
        st.session_state.df_projek = clean_df
        with st.expander("Lihat Data Aktif"):
            st.dataframe(st.session_state.df_projek, use_container_width=True)
    else:
        st.error(msg)
        st.session_state.df_projek = None

is_ready = st.session_state.df_projek is not None

# -- MEMBUAT TAB UNTUK MEMISAHKAN FITUR --
tab1, tab2 = st.tabs(["Optimasi Utama", "Pengujian Parameter (Analisis)"])

# ==========================================
# TAB 1: OPTIMASI UTAMA (OPERASIONAL)
# ==========================================
with tab1:
    st.header("Parameter Algoritma")
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        pop_size = st.number_input("Colony Size", min_value=1, value=3)
        max_iter = st.number_input("Maksimum Iterasi", min_value=1, value=60)
    with col_param2:
        limit = st.number_input("Limit Trial", min_value=1, value=5)
        nse = st.number_input("Number of Sequence (NSE)", min_value=1, value=2)
    
    if st.button("Jalankan Optimasi", type="primary", disabled=not is_ready):
        progress_bar = st.progress(0)
        with st.spinner("Memproses algoritma..."):
            best_seq, best_fit, makespan = run_abc(
                pop_size, max_iter, limit, nse, 
                st.session_state.df_projek, 
                progress_callback=progress_bar.progress
            )
            
            st.session_state.hasil_optimasi = {
                'sequence': best_seq,
                'fitness': best_fit,
                'makespan': makespan
            }

    if st.session_state.hasil_optimasi:
        st.divider()
        res = st.session_state.hasil_optimasi
        df_data = st.session_state.df_projek
        
        if len(res['sequence']) != len(df_data):
            st.warning("Dataset telah berubah. Silakan klik tombol 'Jalankan Optimasi' kembali.")
        else:
            st.header("Hasil Optimasi Penjadwalan")
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Waktu Pengerjaan Total", f"{res['makespan']} Pekan")
            col_res2.metric("Nilai Fitness", f"{res['fitness']:.5f}")
            col_res3.metric("Urutan Terbaik", " ➔ ".join([str(x) for x in res['sequence']]))
            
            df_timetable = calculate_timetable(res['sequence'], df_data)
            st.plotly_chart(generate_gantt_chart(df_timetable), use_container_width=True)
            
            csv_data = convert_df_to_csv(df_timetable)
            st.download_button("Unduh Jadwal (CSV)", data=csv_data, file_name="jadwal_optimasi_abc.csv", mime="text/csv", type="primary")

# ==========================================
# TAB 2: PENGUJIAN PARAMETER (ANALISIS)
# ==========================================
with tab2:
    st.header("Skenario Pengujian Algoritma")
    st.markdown("Fitur ini menjalankan algoritma berulang kali untuk membuktikan parameter mana yang menghasilkan nilai fitness terbaik, sesuai format jurnal.")
    
    test_type = st.radio("Pilih Parameter yang Akan Diuji:", ["Uji Coba Batas Parameter Iterasi", "Uji Coba Batas Parameter Limit"])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if test_type == "Uji Coba Batas Parameter Iterasi":
            input_vals = st.text_input("Nilai Iterasi yang diuji (pisahkan dengan koma):", "10, 20, 30, 40, 50, 60")
            fixed_val = st.number_input("Nilai Limit Tetap:", value=5)
            param_name = "Iterasi"
        else:
            input_vals = st.text_input("Nilai Limit yang diuji (pisahkan dengan koma):", "5, 10, 15, 20, 25, 30")
            fixed_val = st.number_input("Nilai Iterasi Tetap:", value=60)
            param_name = "Limit"
            
    with col_t2:
        num_trials = st.number_input("Jumlah Percobaan per Nilai (Sesuai jurnal = 3):", min_value=1, value=3)
        test_pop_size = st.number_input("Colony Size Tetap:", min_value=1, value=3)
        test_nse = st.number_input("NSE Tetap:", min_value=1, value=2)

    if st.button("Jalankan Pengujian", type="primary", disabled=not is_ready):
        # 1. Parsing input nilai (mengubah teks "10, 20..." menjadi list angka [10, 20...])
        try:
            test_values = [int(v.strip()) for v in input_vals.split(",")]
        except ValueError:
            st.error("Format nilai salah! Pastikan hanya memasukkan angka yang dipisahkan koma.")
            st.stop()

        # 2. Proses Pengujian
        progress_uji = st.progress(0)
        total_runs = len(test_values) * num_trials
        current_run = 0
        
        results_data = []
        
        with st.spinner("Sedang menguji berbagai kombinasi. Ini mungkin memakan waktu..."):
            for val in test_values:
                trial_fitnesses = []
                for t in range(num_trials):
                    # Tentukan parameter mana yang diubah berdasarkan pilihan
                    iter_val = val if test_type == "Uji Coba Batas Parameter Iterasi" else fixed_val
                    limit_val = val if test_type == "Uji Coba Batas Parameter Limit" else fixed_val
                    
                    # Jalankan ABC (matikan progress_callback agar bar UI tidak bertabrakan)
                    _, best_fit, _ = run_abc(test_pop_size, iter_val, limit_val, test_nse, st.session_state.df_projek, progress_callback=None)
                    
                    trial_fitnesses.append(best_fit)
                    
                    current_run += 1
                    progress_uji.progress(current_run / total_runs)
                
                # Menghitung Rata-rata dan merangkum baris tabel
                avg_fitness = sum(trial_fitnesses) / num_trials
                row_data = {param_name: val}
                for i, fit in enumerate(trial_fitnesses):
                    row_data[f'Percobaan ke-{i+1}'] = round(fit, 4)
                row_data['Rata - Rata Fitness'] = round(avg_fitness, 4)
                
                results_data.append(row_data)

        # 3. Menampilkan Tabel Hasil
        df_results = pd.DataFrame(results_data)
        st.success("Pengujian selesai!")
        st.subheader(f"Tabel {test_type}")
        st.dataframe(df_results, use_container_width=True)

        # 4. Membuat Visualisasi Grafik Garis (Line Chart) seperti Jurnal
        st.subheader("Grafik Hasil Pengujian")
        fig = go.Figure()
        
        # Tambahkan garis untuk setiap percobaan
        for i in range(num_trials):
            fig.add_trace(go.Scatter(
                x=df_results[param_name], 
                y=df_results[f'Percobaan ke-{i+1}'], 
                mode='lines+markers', 
                name=f'Percobaan {i+1}'
            ))
            
        # Tambahkan garis Rata-rata yang lebih tebal
        fig.add_trace(go.Scatter(
            x=df_results[param_name], 
            y=df_results['Rata - Rata Fitness'], 
            mode='lines+markers', 
            name='Rata-rata',
            line=dict(width=4, color='purple')
        ))
        
        fig.update_layout(
            title=f"Pengaruh Nilai {param_name} terhadap Fitness",
            xaxis_title=f"Nilai {param_name}",
            yaxis_title="Fitness",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)