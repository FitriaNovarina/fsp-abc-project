import pandas as pd
import numpy as np

import plotly.express as px

def validate_and_preprocess(df):
    if 'Projek' not in df.columns:
        return False, "Gagal: Kolom 'Projek' tidak ditemukan. Pastikan format CSV sesuai.", None
    
    if df.isnull().values.any():
        return False, "Gagal: Terdapat data kosong pada dataset. Harap periksa kembali file Anda.", None
    
    try:
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
    except ValueError:
        return False, "Gagal: Terdapat huruf pada kolom durasi. Harap masukkan angka saja.", None
        
    return True, "Data valid dan siap diproses.", df

def calculate_timetable(sequence, df):
    num_jobs = len(sequence)
    num_stages = len(df.columns) - 1 
    
    start_times = np.zeros((num_jobs, num_stages))
    end_times = np.zeros((num_jobs, num_stages))
    task_data = []
    
    for i in range(num_jobs):
        job_idx = df['Projek'].tolist().index(sequence[i])
        projek_name = f"Projek {sequence[i]}"
        
        for j in range(num_stages):
            duration = df.iloc[job_idx, j+1]
            stage_name = df.columns[j+1]
            
            if i == 0 and j == 0:
                start = 0
            elif i == 0:
                start = end_times[i][j-1]
            elif j == 0:
                start = end_times[i-1][j]
            else:
                start = max(end_times[i-1][j], end_times[i][j-1])
            
            end = start + duration
            start_times[i][j] = start
            end_times[i][j] = end
            
            if duration > 0: 
                task_data.append({
                    'Projek': projek_name,
                    'Tahap': stage_name,
                    'Mulai': start,
                    'Selesai': end,
                    'Durasi (Pekan)': duration
                })
                
    return pd.DataFrame(task_data)

def generate_gantt_chart(df_timetable):
    fig = px.bar(
        df_timetable, 
        base="Mulai", 
        x="Durasi (Pekan)", 
        y="Tahap", 
        color="Projek", 
        orientation='h',
        title="Gantt Chart Jadwal Pengerjaan Projek",
        text="Projek",
        labels={"Tahap": "Tahapan Pengerjaan", "Durasi (Pekan)": "Pekan ke-"}
    )
    fig.update_layout(barmode='overlay', xaxis_title="Waktu (Pekan)", yaxis_title="Tahapan")
    fig.update_yaxes(autorange="reversed") 
    
    return fig

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')