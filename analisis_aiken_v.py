import pandas as pd

# ==================================================
# 1. Membaca data validasi ahli dari file Excel
#    File diambil langsung dari GitHub (link RAW)
# ==================================================
file_path = "https://raw.githubusercontent.com/arikaps/analisasoal/main/data_validasi_siappython.xlsx"

df = pd.read_excel(file_path)

# ==================================================
# 2. Menentukan parameter skala Aiken’s V
#    Skala penilaian 1–5
# ==================================================
lo = 1          # skor terendah pada skala
c = 5           # jumlah kategori penilaian
validator_cols = ["Skor_V1", "Skor_V2"]  # kolom penilaian dari 2 ahli
n = len(validator_cols)                  # jumlah validator

# ==================================================
# 3. Menghitung nilai Aiken’s V
# ==================================================
# Menghitung nilai s = r - lo
s = df[validator_cols] - lo
s.columns = [f"s_{col}" for col in validator_cols]

# Rumus Aiken’s V
aiken_v = s.sum(axis=1) / (n * (c - 1))

# ==================================================
# 4. Menggabungkan hasil perhitungan ke DataFrame
# ==================================================
df_output = pd.concat([df, s], axis=1)
df_output["Aiken_V"] = aiken_v

# ==================================================
# 5. Menentukan kategori relevansi berdasarkan Aiken’s V
# ==================================================
def kategori_relevansi(v):
    if v <= 0.20:
        return "Kurang Relevan"
    elif v <= 0.40:
        return "Tidak Relevan"
    elif v <= 0.60:
        return "Cukup Relevan"
    elif v <= 0.80:
        return "Relevan"
    else:
        return "Sangat Relevan"

df_output["Kategori_Relevansi"] = df_output["Aiken_V"].apply(kategori_relevansi)

# ==================================================
# 6. Menghitung rata-rata Aiken’s V untuk setiap soal
# ==================================================
aiken_per_soal = (
    df_output.groupby("No_Soal")["Aiken_V"]
    .mean()
    .reset_index(name="Aiken_V_Rata2")
)

# ==================================================
# 7. Menyimpan hasil analisis ke file Excel
# ==================================================
output_file = "/content/analisasoal/hasil_aiken_v_relevansi2.xlsx"
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    # Sheet 1: hasil Aiken’s V per indikator/butir
    df_output.to_excel(
        writer,
        sheet_name="Aiken_per_Indikator",
        index=False
    )
    # Sheet 2: rata-rata Aiken’s V per soal
    aiken_per_soal.to_excel(
        writer,
        sheet_name="Aiken_per_Soal",
        index=False
    )

print(f"Hasil Aiken’s V berhasil disimpan ke file: {output_file}")

# ==================================================
# 8. Menampilkan hasil di Python (opsional)
# ==================================================
df_output
