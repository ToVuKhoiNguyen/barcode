import csv
import sqlite3

# Kết nối tới cơ sở dữ liệu SQLite
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Mở tệp CSV và đọc dữ liệu
with open('products.csv', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        barcode_code = row['Barcode Code']
        product_name = row['Product Name']
        price = float(row['Price'])  # Chuyển giá thành số thực
        # Chèn dữ liệu vào bảng sản phẩm
        cursor.execute('''
        INSERT INTO products (barcode_code, product_name, price)
        VALUES (?, ?, ?)
        ''', (barcode_code, product_name, price))

# Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("Dữ liệu đã được nhập vào cơ sở dữ liệu thành công.")
