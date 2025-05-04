import sqlite3

# Kết nối đến file database
conn = sqlite3.connect('products.db')
c = conn.cursor()

# Truy vấn tất cả dữ liệu từ bảng products
c.execute("SELECT * FROM products")
rows = c.fetchall()

# Hiển thị dữ liệu
print("DANH SÁCH SẢN PHẨM TRONG DATABASE:")
print("Barcode | Tên sản phẩm | Giá")
print("----------------------------------------")
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]} VND")

conn.close()
