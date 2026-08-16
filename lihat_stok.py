import sqlite3

def lihat_semua_stok():
    conn = sqlite3.connect("stok.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            produk.id,
            produk.nama,
            produk.sku,
            produk.stok_minimum,
            COALESCE(SUM(CASE WHEN transaksi.jenis = 'masuk' THEN transaksi.jumlah ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN transaksi.jenis = 'keluar' THEN transaksi.jumlah ELSE 0 END), 0) AS stok_sekarang
        FROM produk
        LEFT JOIN transaksi ON produk.id = transaksi.produk_id
        GROUP BY produk.id
    """)

    hasil = cursor.fetchall()
    conn.close()

    print(f"{'ID':<4}{'Nama':<20}{'SKU':<10}{'Stok Sekarang':<15}{'Status'}")
    print("-" * 65)
    for row in hasil:
        id_produk, nama, sku, stok_minimum, stok_sekarang = row
        status = "⚠️ MENIPIS" if stok_sekarang <= stok_minimum else "✅ Aman"
        print(f"{id_produk:<4}{nama:<20}{sku:<10}{stok_sekarang:<15}{status}")

if __name__ == "__main__":
    lihat_semua_stok()