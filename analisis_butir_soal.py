# ==================================================
# ANALISIS BUTIR SOAL LENGKAP
# (Kesukaran, Daya Beda, KR-20, Distractor)
# Kunci diambil dari Sheet ke-3 (kunci)
# ==================================================

import pandas as pd
import numpy as np
import os

# ==================================================
# 1. BACA FILE EXCEL (3 SHEET)
# ==================================================
file_path = (
    "https://raw.githubusercontent.com/"
    "arikaps/analisasoal/main/jawaban_siswa_nilai_opsi_kunci.xlsx"
)

df_nilai = pd.read_excel(file_path, sheet_name="nilai")
df_opsi  = pd.read_excel(file_path, sheet_name="opsi")
df_kunci = pd.read_excel(file_path, sheet_name="kunci")

# Buat dictionary kunci
kunci_dict = dict(zip(df_kunci["no_soal"].astype(str).apply(lambda x: f"S{x}"), df_kunci["kunci"])) # Changed 'Butir_Soal' to 'no_soal' and 'Kunci' to 'kunci', and converted 'no_soal' to 'S{no_soal}' format

item_cols = [c for c in df_nilai.columns if c.startswith("S")]
n_items = len(item_cols)
n_peserta = len(df_nilai)

# ==================================================
# 2. SKOR TOTAL
# ==================================================
df_nilai["Skor_Total"] = df_nilai[item_cols].sum(axis=1)

# ==================================================
# 3. TINGKAT KESUKARAN
# ==================================================
p = df_nilai[item_cols].mean()

def kategori_kesukaran(x):
    if x < 0.30:
        return "Sukar"
    elif x <= 0.70:
        return "Sedang"
    else:
        return "Mudah"

kategori_p = p.apply(kategori_kesukaran)

# ==================================================
# 4. DAYA PEMBEDA (27%)
# ==================================================
df_sorted = df_nilai.sort_values("Skor_Total", ascending=False)
n_kelompok = int(round(0.27 * n_peserta))

kelompok_atas = df_sorted.head(n_kelompok)
kelompok_bawah = df_sorted.tail(n_kelompok)

d = kelompok_atas[item_cols].mean() - kelompok_bawah[item_cols].mean()

def kategori_daya_beda(x):
    if x >= 0.40:
        return "Sangat Baik"
    elif x >= 0.30:
        return "Baik"
    elif x >= 0.20:
        return "Cukup"
    else:
        return "Jelek"

kategori_d = d.apply(kategori_daya_beda)

# ==================================================
# 5. KEPUTUSAN BUTIR
# ==================================================
def keputusan_butir(p, d):
    if 0.30 <= p <= 0.80 and d >= 0.30:
        return "Diterima"
    elif d >= 0.20:
        return "Direvisi"
    else:
        return "Dibuang"

keputusan = [keputusan_butir(p[i], d[i]) for i in item_cols]

analisis_butir = pd.DataFrame({
    "Butir_Soal": item_cols,
    "Tingkat_Kesukaran": p.values,
    "Kategori_Kesukaran": kategori_p.values,
    "Daya_Pembeda": d.values,
    "Kategori_Daya_Beda": kategori_d.values,
    "Keputusan": keputusan
})

# ==================================================
# 6. RELIABILITAS KR-20
# ==================================================
q = 1 - p
var_total = df_nilai["Skor_Total"].var(ddof=1)

kr20 = (n_items / (n_items - 1)) * (1 - (np.sum(p * q) / var_total))

def interpretasi_reliabilitas(r):
    if r >= 0.90:
        return "Sangat Tinggi"
    elif r >= 0.70:
        return "Tinggi"
    elif r >= 0.50:
        return "Sedang"
    else:
        return "Rendah"

df_reliabilitas = pd.DataFrame({
    "Jenis_Reliabilitas": ["KR-20"],
    "Nilai_Reliabilitas": [round(kr20, 3)],
    "Interpretasi": [interpretasi_reliabilitas(kr20)]
})

# ==================================================
# 7. ANALISIS DISTRACTOR (NON-KUNCI)
# ==================================================
distractor_data = []

for item in item_cols:
    kunci = kunci_dict[item]
    distribusi = df_opsi[item].value_counts()
    total = distribusi.sum()

    for opsi in ["A", "B", "C", "D", "E"]:
        if opsi == kunci:
            continue  # kunci bukan distractor

        frek = distribusi.get(opsi, 0)
        proporsi = frek / total

        status = "Berfungsi" if proporsi >= 0.05 else "Tidak Berfungsi"

        distractor_data.append({
            "Butir_Soal": item,
            "Opsi_Distractor": opsi,
            "Frekuensi": frek,
            "Proporsi": round(proporsi, 3),
            "Status_Distractor": status
        })

df_distractor = pd.DataFrame(distractor_data)

# ==================================================
# 8. SIMPAN KE EXCEL
# ==================================================
output_dir = "/content/analisasoal"
os.makedirs(output_dir, exist_ok=True)

output_file = f"{output_dir}/hasil_analisis_butir_lengkap.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_nilai[["ID_Peserta", "Skor_Total"]].to_excel(
        writer, sheet_name="Skor_Peserta", index=False
    )
    analisis_butir.to_excel(
        writer, sheet_name="Analisis_Butir", index=False
    )
    df_reliabilitas.to_excel(
        writer, sheet_name="Reliabilitas", index=False
    )
    df_distractor.to_excel(
        writer, sheet_name="Analisis_Distractor", index=False
    )

# ==================================================
# 9. RINGKASAN
# ==================================================
print("✅ ANALISIS SELESAI")
print(f"📁 File tersimpan di: {output_file}")
print(f"Jumlah Peserta : {n_peserta}")
print(f"Jumlah Butir   : {n_items}")
print(f"Reliabilitas KR-20 : {kr20:.3f} ({interpretasi_reliabilitas(kr20)})")
