import sqlite3
from datetime import date

def tambah_produk(nama, sku, kategori, satuan, stok_minimum):
    conn = sqlite3.connect("stok.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produk (nama, sku, kategori, satuan, stok_minimum) VALUES (?, ?, ?, ?, ?)",
        (nama, sku, kategori, satuan, stok_minimum)
    )
    conn.commit()
    conn.close()
    print(f"Produk '{nama}' berhasil ditambahkan!")

def tambah_transaksi(produk_id, jenis, jumlah):
    conn = sqlite3.connect("stok.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transaksi (produk_id, jenis, jumlah, tanggal) VALUES (?, ?, ?, ?)",
        (produk_id, jenis, jumlah, str(date.today()))
    )
    conn.commit()
    conn.close()
    print(f"Transaksi '{jenis}' sebanyak {jumlah} berhasil dicatat!")

if __name__ == "__main__":
    # Contoh: tambah 1 produk
    tambah_produk("Indomie Goreng", "SKU001", "Makanan", "pcs", 20)

    # Contoh: catat stok masuk 100 pcs untuk produk dengan id=1
    tambah_transaksi(1, "masuk", 100)