import sqlite3

def init_db():
    conn = sqlite3.connect("stok.db")
    cursor = conn.cursor()

    # Tabel Produk: daftar master semua barang
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            kategori TEXT,
            satuan TEXT,
            stok_minimum INTEGER DEFAULT 0
        )
    """)

    # Tabel Transaksi: catatan tiap barang masuk/keluar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produk_id INTEGER NOT NULL,
            jenis TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            FOREIGN KEY (produk_id) REFERENCES produk (id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database berhasil dibuat!")

if __name__ == "__main__":
    init_db()