import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Aplikasi Peminjaman Barang", layout="wide")

# ------------------- INISIALISASI DATA -------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame({
        "Kode Barang": ["SDS001", "SDS002"],
        "Nama Barang": ["Laptop", "Mouse" ],
        "Stok": [1, 1]
    })

if "peminjaman" not in st.session_state:
    st.session_state.peminjaman = pd.DataFrame(
        columns=["ID Pinjam", "Nama Peminjam", "Kode Barang", "Nama Barang",
                 "Jumlah", "Tanggal Pinjam", "Status"]
    )

st.title("📦 Aplikasi Peminjaman Barang")

# ------------------- LIST BARANG -------------------
st.header("📋 Daftar Barang")
st.dataframe(st.session_state.inventory, use_container_width=True)

# ------------------- FORM PEMINJAMAN -------------------
st.header("Form Peminjaman")
with st.form("form_pinjam"):
    peminjam = st.text_input("Nama Peminjam")
    barang_list = st.session_state.inventory["Kode Barang"].tolist()
    kode_barang = st.selectbox("Pilih Kode Barang", barang_list)

    # tampilkan nama barang otomatis
    if kode_barang:
        idx = st.session_state.inventory[st.session_state.inventory["Kode Barang"] == kode_barang].index[0]
        nama_barang = st.session_state.inventory.at[idx, "Nama Barang"]
        stok_tersedia = st.session_state.inventory.at[idx, "Stok"]
        st.info(f"Nama Barang: **{nama_barang}** | Stok Tersedia: {stok_tersedia}")

    jumlah = st.number_input("Jumlah Pinjam", min_value=1, step=1)
    submit_pinjam = st.form_submit_button("Pinjam Barang")

    if submit_pinjam:
        if peminjam == "":
            st.error("Nama peminjam tidak boleh kosong!")
        elif jumlah > stok_tersedia:
            st.error("❌ Stok tidak mencukupi!")
        else:
            # kurangi stok
            st.session_state.inventory.at[idx, "Stok"] -= jumlah

            # buat ID pinjam
            id_pinjam = f"PJM{len(st.session_state.peminjaman)+1:03d}"

            # catat peminjaman
            new_pinjam = pd.DataFrame({
                "ID Pinjam": [id_pinjam],
                "Nama Peminjam": [peminjam],
                "Kode Barang": [kode_barang],
                "Nama Barang": [nama_barang],
                "Jumlah": [jumlah],
                "Tanggal Pinjam": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                "Status": ["Dipinjam"]
            })
            st.session_state.peminjaman = pd.concat(
                [st.session_state.peminjaman, new_pinjam],
                ignore_index=True
            )

            st.success(f"✅ {jumlah} {nama_barang} berhasil dipinjam oleh {peminjam}")

# ------------------- DATA PEMINJAMAN -------------------
st.header("📑 Data Peminjaman")
st.dataframe(st.session_state.peminjaman, use_container_width=True)

# tombol download data peminjaman
if not st.session_state.peminjaman.empty:
    csv_pjm = st.session_state.peminjaman.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Data Peminjaman (CSV)",
                       data=csv_pjm,
                       file_name="data_peminjaman.csv",
                       mime="text/csv")

# ------------------- PENGEMBALIAN -------------------
st.header("🔄 Pengembalian Barang")
id_list = st.session_state.peminjaman[st.session_state.peminjaman["Status"] == "Dipinjam"]["ID Pinjam"].tolist()

if id_list:
    pilih_id = st.selectbox("Pilih ID Pinjam", id_list)
    if st.button("Kembalikan Barang"):
        idx_pjm = st.session_state.peminjaman[st.session_state.peminjaman["ID Pinjam"] == pilih_id].index[0]
        kode_barang = st.session_state.peminjaman.at[idx_pjm, "Kode Barang"]
        jumlah = st.session_state.peminjaman.at[idx_pjm, "Jumlah"]

        # tambahkan stok kembali
        idx_inv = st.session_state.inventory[st.session_state.inventory["Kode Barang"] == kode_barang].index[0]
        st.session_state.inventory.at[idx_inv, "Stok"] += jumlah

        # update status peminjaman
        st.session_state.peminjaman.at[idx_pjm, "Status"] = "Dikembalikan"

        st.success(f"✅ Barang dengan ID {pilih_id} berhasil dikembalikan.")
else:
    st.info("Belum ada barang yang sedang dipinjam.")

# ------------------- BACKUP & RESTORE -------------------
st.sidebar.header("⚙️ Backup & Restore Data")

# Download inventory
csv_inv = st.session_state.inventory.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("⬇️ Download Inventory (CSV)",
                           data=csv_inv,
                           file_name="inventory.csv",
                           mime="text/csv")

# Download peminjaman
csv_pjm = st.session_state.peminjaman.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("⬇️ Download Peminjaman (CSV)",
                           data=csv_pjm,
                           file_name="peminjaman.csv",
                           mime="text/csv")

# Upload untuk restore
upload_inv = st.sidebar.file_uploader("🔄 Upload Inventory (CSV)", type=["csv"])
if upload_inv:
    st.session_state.inventory = pd.read_csv(upload_inv)
    st.sidebar.success("✅ Inventory berhasil di-restore!")

upload_pjm = st.sidebar.file_uploader("🔄 Upload Peminjaman (CSV)", type=["csv"])
if upload_pjm:
    st.session_state.peminjaman = pd.read_csv(upload_pjm)
    st.sidebar.success("✅ Data peminjaman berhasil di-restore!")
