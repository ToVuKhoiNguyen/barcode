import sqlite3

# Kết nối tới cơ sở dữ liệu SQLite
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Tạo bảng sản phẩm
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    barcode_code TEXT PRIMARY KEY,
    product_name TEXT,
    price REAL
)
''')

# Commit thay đổi và đóng kết nối
conn.commit()
conn.close()

print("Cơ sở dữ liệu và bảng sản phẩm đã được tạo thành công.")
