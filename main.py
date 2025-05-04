import cv2
import csv
import time
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime

# --- Đọc dữ liệu sản phẩm từ CSV ---
def load_product_data_from_csv(filename='products.csv'):
    products = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            barcode = row['Barcode Code'].strip()
            name = row['Product Name'].strip()
            price = int(row['Price'])
            products[barcode] = {'name': name, 'price': price}
    return products

# --- Cấu hình ---
cooldown = 3  # giây chống quét trùng

# --- Biến toàn cục ---
cart = {}
last_scanned_time = {}
product_data = load_product_data_from_csv()
cap = cv2.VideoCapture(0)

# --- Giao diện Tkinter ---
def update_receipt():
    # Cập nhật hóa đơn trên GUI
    total = 0
    receipt_text.delete(1.0, tk.END)  # Xóa hóa đơn cũ
    receipt_text.insert(tk.END, "======== HÓA ĐƠN TẠM THỜI ========\n")
    receipt_text.insert(tk.END, "{:<25} {:>10} {:>10}\n".format("Tên sản phẩm", "Giá", "Số lượng"))
    receipt_text.insert(tk.END, "-" * 50 + "\n")
    
    for item in cart.values():
        line_total = item['price'] * item['quantity']
        receipt_text.insert(tk.END, "{:<25} {:>10,} {:>10}\n".format(item['name'], item['price'], item['quantity']))
        total += line_total
        
    receipt_text.insert(tk.END, "-" * 50 + "\n")
    receipt_text.insert(tk.END, "{:<25} {:>10,} VND\n".format("TỔNG TIỀN", total))
    receipt_text.insert(tk.END, "===================================\n")

def remove_item_from_cart():
    # Loại bỏ sản phẩm đã chọn khỏi giỏ hàng
    selected_item = cart_listbox.curselection()
    if selected_item:
        barcode = cart_listbox.get(selected_item)
        del cart[barcode]
        update_receipt()
        update_cart_listbox()

def update_cart_listbox():
    # Cập nhật danh sách sản phẩm trong giỏ hàng (dùng Listbox)
    cart_listbox.delete(0, tk.END)
    for barcode, item in cart.items():
        cart_listbox.insert(tk.END, f"{item['name']} - {item['quantity']} x {item['price']} VND")

def edit_item_quantity():
    # Sửa số lượng sản phẩm
    selected_item = cart_listbox.curselection()
    if selected_item:
        barcode = cart_listbox.get(selected_item)
        new_quantity = simpledialog.askinteger("Sửa số lượng", f"Sửa số lượng cho sản phẩm {cart[barcode]['name']}:",
                                               minvalue=1, initialvalue=cart[barcode]['quantity'])
        if new_quantity is not None:
            cart[barcode]['quantity'] = new_quantity
            update_receipt()
            update_cart_listbox()

# --- Tạo cửa sổ Tkinter ---
root = tk.Tk()
root.title("Hóa Đơn Thời Gian Thực")

# Cài đặt kích thước cửa sổ
root.geometry("500x500")

# Khung hiển thị hóa đơn
receipt_text = tk.Text(root, height=15, width=50, wrap=tk.WORD)
receipt_text.pack(pady=20)

# Danh sách sản phẩm trong giỏ hàng
cart_listbox = tk.Listbox(root, width=50, height=10)
cart_listbox.pack(pady=10)

# Nút lưu hóa đơn vào file
def save_receipt():
    if cart:
        # Tạo tên file theo định dạng "receipt_YYYY-MM-DD_HH-MM-SS.txt"
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"receipt_{current_time}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("======== HÓA ĐƠN CUỐI CÙNG ========\n")
            total = 0
            f.write("{:<25} {:>10} {:>10}\n".format("Tên sản phẩm", "Giá", "Số lượng"))
            f.write("-" * 50 + "\n")
            for item in cart.values():
                line_total = item['price'] * item['quantity']
                f.write("{:<25} {:>10,} {:>10}\n".format(item['name'], item['price'], item['quantity']))
                total += line_total
            f.write("-" * 50 + "\n")
            f.write("{:<25} {:>10,} VND\n".format("TỔNG TIỀN", total))
            f.write("===================================\n")
        print(f"📝 Hóa đơn đã được lưu vào file: {filename}")

# Nút lưu hóa đơn
save_button = tk.Button(root, text="Lưu Hóa Đơn", command=save_receipt)
save_button.pack(pady=10)

# Nút xóa sản phẩm khỏi giỏ hàng
remove_button = tk.Button(root, text="Xóa Sản Phẩm", command=remove_item_from_cart)
remove_button.pack(pady=10)

# Nút sửa số lượng sản phẩm
edit_button = tk.Button(root, text="Sửa Số Lượng", command=edit_item_quantity)
edit_button.pack(pady=10)

# --- Vòng lặp chính ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    barcodes = decode(frame)
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        barcode_data = barcode.data.decode("utf-8")
        current_time = time.time()
        last_time = last_scanned_time.get(barcode_data, 0)

        if current_time - last_time < cooldown:
            continue
        last_scanned_time[barcode_data] = current_time

        if barcode_data in product_data:
            product = product_data[barcode_data]
            name = product['name']
            price = product['price']

            if barcode_data not in cart:
                cart[barcode_data] = {'name': name, 'price': price, 'quantity': 1}
            else:
                cart[barcode_data]['quantity'] += 1

            # Cập nhật hóa đơn tạm thời
            update_receipt()

            # Cập nhật danh sách giỏ hàng trong Listbox
            update_cart_listbox()

            # Hiển thị thông tin trên camera
            text = f"{name} - {price} VND"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y - 10 if y > 20 else y + h + 30
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# --- Chạy giao diện Tkinter ---
root.mainloop()
