import csv
import sqlite3

def import_csv_to_db(filename='products.csv'):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Mở tệp CSV và đọc dữ liệu
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            barcode = row['Barcode Code'].strip()
            name = row['Product Name'].strip()
            price = int(row['Price'])
            
            # Chèn hoặc cập nhật dữ liệu vào cơ sở dữ liệu
            c.execute('''
                INSERT OR REPLACE INTO products (barcode, name, price) 
                VALUES (?, ?, ?)
            ''', (barcode, name, price))

    conn.commit()
    conn.close()
    print("Dữ liệu đã được nhập vào cơ sở dữ liệu thành công.")

if __name__ == "__main__":
    import_csv_to_db()
