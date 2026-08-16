from notifikasi import kirim_notifikasi
import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

st.set_page_config(page_title="Sistem Stok Barang", layout="wide")

def get_conn():
    return sqlite3.connect("stok.db")

def lihat_semua_stok():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT 
            produk.id, produk.nama, produk.sku, produk.kategori,
            produk.satuan, produk.stok_minimum,
            COALESCE(SUM(CASE WHEN transaksi.jenis = 'masuk' THEN transaksi.jumlah ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN transaksi.jenis = 'keluar' THEN transaksi.jumlah ELSE 0 END), 0) AS stok_sekarang
        FROM produk
        LEFT JOIN transaksi ON produk.id = transaksi.produk_id
        GROUP BY produk.id
    """, conn)
    conn.close()
    return df

def lihat_riwayat_transaksi():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT transaksi.id, produk.nama AS produk, transaksi.jenis,
               transaksi.jumlah, transaksi.tanggal
        FROM transaksi
        JOIN produk ON produk.id = transaksi.produk_id
        ORDER BY transaksi.id DESC
    """, conn)
    conn.close()
    return df

def tambah_produk(nama, sku, kategori, satuan, stok_minimum):
    conn = get_conn()
    conn.execute(
        "INSERT INTO produk (nama, sku, kategori, satuan, stok_minimum) VALUES (?, ?, ?, ?, ?)",
        (nama, sku, kategori, satuan, stok_minimum)
    )
    conn.commit()
    conn.close()

def update_produk(produk_id, nama, sku, kategori, satuan, stok_minimum):
    conn = get_conn()
    conn.execute(
        "UPDATE produk SET nama=?, sku=?, kategori=?, satuan=?, stok_minimum=? WHERE id=?",
        (nama, sku, kategori, satuan, stok_minimum, produk_id)
    )
    conn.commit()
    conn.close()

def hapus_produk(produk_id):
    conn = get_conn()
    conn.execute("DELETE FROM transaksi WHERE produk_id=?", (produk_id,))
    conn.execute("DELETE FROM produk WHERE id=?", (produk_id,))
    conn.commit()
    conn.close()

def tambah_transaksi(produk_id, jenis, jumlah):
    conn = get_conn()
    conn.execute(
        "INSERT INTO transaksi (produk_id, jenis, jumlah, tanggal) VALUES (?, ?, ?, ?)",
        (produk_id, jenis, jumlah, str(date.today()))
    )
    conn.commit()
    conn.close()

# ---------- TAMPILAN WEB ----------

st.title("📦 Sistem Manajemen Stok")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Lihat Stok", "➕ Tambah Produk", "✏️ Kelola Produk",
    "🔄 Catat Transaksi", "📜 Riwayat Transaksi"
])

with tab1:
    st.subheader("Stok Saat Ini")
    df = lihat_semua_stok()
    if df.empty:
        st.info("Belum ada produk.")
    else:
        df["status"] = df.apply(
            lambda r: "⚠️ MENIPIS" if r["stok_sekarang"] <= r["stok_minimum"] else "✅ Aman",
            axis=1
        )
        st.dataframe(df, use_container_width=True)
        menipis = df[df["stok_sekarang"] <= df["stok_minimum"]]
        if not menipis.empty:
            st.warning(f"⚠️ {len(menipis)} produk stoknya menipis: " + ", ".join(menipis["nama"]))

with tab2:
    st.subheader("Tambah Produk Baru")
    with st.form("form_produk"):
        nama = st.text_input("Nama Produk")
        sku = st.text_input("SKU (kode unik)")
        kategori = st.text_input("Kategori")
        satuan = st.text_input("Satuan (pcs/kg/box)")
        stok_minimum = st.number_input("Stok Minimum (batas alert)", min_value=0, value=10)
        submit = st.form_submit_button("Simpan Produk")
        if submit:
            if nama and sku:
                tambah_produk(nama, sku, kategori, satuan, stok_minimum)
                st.success(f"Produk '{nama}' berhasil ditambahkan!")
                st.rerun()
            else:
                st.error("Nama dan SKU wajib diisi.")

with tab3:
    st.subheader("Edit atau Hapus Produk")
    df = lihat_semua_stok()
    if df.empty:
        st.info("Belum ada produk.")
    else:
        pilihan = st.selectbox("Pilih Produk", df["nama"] + " (ID: " + df["id"].astype(str) + ")", key="edit_select")
        produk_id = int(pilihan.split("ID: ")[1].replace(")", ""))
        row = df[df["id"] == produk_id].iloc[0]

        with st.form("form_edit"):
            nama_e = st.text_input("Nama Produk", value=row["nama"])
            sku_e = st.text_input("SKU", value=row["sku"])
            kategori_e = st.text_input("Kategori", value=row["kategori"] or "")
            satuan_e = st.text_input("Satuan", value=row["satuan"] or "")
            stok_minimum_e = st.number_input("Stok Minimum", min_value=0, value=int(row["stok_minimum"]))
            col1, col2 = st.columns(2)
            simpan = col1.form_submit_button("💾 Simpan Perubahan")
            hapus = col2.form_submit_button("🗑️ Hapus Produk")

            if simpan:
                update_produk(produk_id, nama_e, sku_e, kategori_e, satuan_e, stok_minimum_e)
                st.success("Perubahan disimpan!")
                st.rerun()
            if hapus:
                hapus_produk(produk_id)
                st.success(f"Produk '{row['nama']}' dan riwayat transaksinya dihapus!")
                st.rerun()

with tab4:
    st.subheader("Catat Stok Masuk / Keluar")
    df = lihat_semua_stok()
    if df.empty:
        st.info("Tambah produk dulu di tab sebelah.")
    else:
        with st.form("form_transaksi"):
            produk_pilihan = st.selectbox("Pilih Produk", df["nama"] + " (ID: " + df["id"].astype(str) + ")")
            produk_id = int(produk_pilihan.split("ID: ")[1].replace(")", ""))
            jenis = st.radio("Jenis Transaksi", ["masuk", "keluar"])
            jumlah = st.number_input("Jumlah", min_value=1, value=1)
            submit2 = st.form_submit_button("Catat Transaksi")
            if submit2:
                tambah_transaksi(produk_id, jenis, jumlah)
                st.success(f"Transaksi '{jenis}' sebanyak {jumlah} berhasil dicatat!")

                # Cek apakah stok jadi menipis setelah transaksi ini
                df_terbaru = lihat_semua_stok()
                produk_terbaru = df_terbaru[df_terbaru["id"] == produk_id].iloc[0]
                if produk_terbaru["stok_sekarang"] <= produk_terbaru["stok_minimum"]:
                    pesan = (
                        f"⚠️ *Stok Menipis!*\n"
                        f"Produk: {produk_terbaru['nama']}\n"
                        f"Sisa stok: {produk_terbaru['stok_sekarang']} {produk_terbaru['satuan'] or ''}\n"
                        f"Batas minimum: {produk_terbaru['stok_minimum']}"
                    )
                    if kirim_notifikasi(pesan):
                        st.info("📱 Notifikasi Telegram terkirim!")

                st.rerun()

with tab5:
    st.subheader("Riwayat Semua Transaksi")
    df_riwayat = lihat_riwayat_transaksi()
    if df_riwayat.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_riwayat, use_container_width=True)