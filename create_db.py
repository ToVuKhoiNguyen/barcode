import sqlite3

def create_database():
    # Tạo kết nối đến cơ sở dữ liệu (nếu chưa có, sẽ tạo mới)
    conn = sqlite3.connect('products.db') 
    c = conn.cursor()

    # Xóa bảng cũ nếu có
    c.execute('DROP TABLE IF EXISTS products')

    # Tạo bảng để lưu trữ sản phẩm
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,  -- Mã vạch
            name TEXT NOT NULL,        -- Tên sản phẩm
            price INTEGER NOT NULL     -- Giá sản phẩm
        )
    ''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Cơ sở dữ liệu đã được tạo thành công.")
