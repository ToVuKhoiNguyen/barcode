import cv2
import csv
import time
import requests
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime
from PIL import Image, ImageTk

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

# --- Gửi hóa đơn lên web Flask ---
def send_receipt_to_web():
    items = []
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
        items.append({
            "name": item['name'],
            "price": item['price'],
            "quantity": item['quantity']
        })
    payload = {"items": items, "total": total}
    try:
        requests.post("http://127.0.0.1:5000/update_receipt", json=payload)
    except Exception as e:
        print("❌ Không gửi được hóa đơn đến web:", e)

# --- Giao diện Tkinter ---
def update_receipt():
    total = 0
    receipt_text.delete(1.0, tk.END)
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
    selected_item = cart_listbox.curselection()
    if selected_item:
        name = cart_listbox.get(selected_item).split(" - ")[0]
        for barcode, item in list(cart.items()):
            if item['name'] == name:
                del cart[barcode]
                break
        update_receipt()
        update_cart_listbox()
        send_receipt_to_web()

def edit_item_quantity():
    selected_item = cart_listbox.curselection()
    if selected_item:
        name = cart_listbox.get(selected_item).split(" - ")[0]
        for barcode, item in cart.items():
            if item['name'] == name:
                new_quantity = simpledialog.askinteger("Sửa số lượng", f"Sửa số lượng cho {item['name']}:", minvalue=1, initialvalue=item['quantity'])
                if new_quantity is not None:
                    cart[barcode]['quantity'] = new_quantity
                    update_receipt()
                    update_cart_listbox()
                    send_receipt_to_web()
                break

def update_cart_listbox():
    cart_listbox.delete(0, tk.END)
    for item in cart.values():
        cart_listbox.insert(tk.END, f"{item['name']} - {item['quantity']} x {item['price']} VND")

def save_receipt():
    if cart:
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
        print(f"📝 Hóa đơn đã được lưu: {filename}")

# --- Tạo cửa sổ chính ---
root = tk.Tk()
root.title("Quét Mã vạch và Hóa Đơn")
root.geometry("1000x600")

# --- Khung trái: Camera ---
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

video_label = tk.Label(left_frame)
video_label.pack()

# --- Khung phải: Hóa đơn ---
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

receipt_text = tk.Text(right_frame, height=15, width=50, wrap=tk.WORD)
receipt_text.pack(pady=5)

cart_listbox = tk.Listbox(right_frame, width=50, height=8)
cart_listbox.pack(pady=5)

tk.Button(right_frame, text="Lưu Hóa Đơn", command=save_receipt).pack(pady=2)
tk.Button(right_frame, text="Xóa Sản Phẩm", command=remove_item_from_cart).pack(pady=2)
tk.Button(right_frame, text="Sửa Số Lượng", command=edit_item_quantity).pack(pady=2)

# --- Cập nhật video ---
def update_camera():
    ret, frame = cap.read()
    if ret:
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

                update_receipt()
                update_cart_listbox()
                send_receipt_to_web()

                text = f"{name} - {price} VND"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y - 10 if y > 20 else y + h + 30
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Hiển thị lên giao diện Tkinter
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    root.after(10, update_camera)

# --- Khởi động vòng lặp camera và GUI ---
update_camera()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
