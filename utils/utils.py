import pandas as pd
import numpy as np
import re

import plotly.express as px

def validate_and_preprocess(df):
    # Pastikan ada kolom Projek; jika tidak persis, gunakan kolom pertama atau nama mirip
    cols_lower = [c.lower() for c in df.columns]
    if 'projek' in cols_lower:
        projek_col = df.columns[cols_lower.index('projek')]
        if projek_col != 'Projek':
            df = df.rename(columns={projek_col: 'Projek'})
    else:
        # Asumsikan kolom pertama adalah kolom projek
        first_col = df.columns[0]
        if first_col != 'Projek':
            df = df.rename(columns={first_col: 'Projek'})

    # Normalisasi nilai pada kolom 'Projek'
    # Contoh input: 'J1', 'J2', '1', 'Proj-3' -> keluaran numeric 1,2,3
    orig_vals = df['Projek'].astype(str).tolist()
    assigned = {}
    used_nums = set()
    next_seq = 1
    for v in orig_vals:
        if v in assigned:
            continue
        s = str(v).strip()
        m = re.search(r"(\d+)", s)
        if m:
            num = int(m.group(1))
            assigned[v] = num
            used_nums.add(num)
        else:
            # cari nomor unused berikutnya
            while next_seq in used_nums:
                next_seq += 1
            assigned[v] = next_seq
            used_nums.add(next_seq)
            next_seq += 1

    df['Projek'] = df['Projek'].astype(str).map(assigned).astype(int)

    # Pastikan kolom 'Projek' adalah kolom pertama
    cols = df.columns.tolist()
    if cols[0] != 'Projek':
        cols.remove('Projek')
        cols = ['Projek'] + cols
        df = df[cols]

    # Konversi kolom durasi tahap menjadi numeric
    non_projek_cols = [c for c in df.columns if c != 'Projek']
    try:
        for col in non_projek_cols:
            df[col] = pd.to_numeric(df[col])
    except Exception:
        return False, f"Gagal: Kolom '{col}' mengandung nilai non-numerik. Harap masukkan angka saja.", None

    # Periksa nilai kosong setelah konversi
    if df.isnull().values.any():
        return False, "Gagal: Terdapat data kosong pada dataset setelah pra-proses. Harap periksa kembali file Anda.", None

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