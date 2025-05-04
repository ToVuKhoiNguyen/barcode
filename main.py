import cv2
import time
import requests
import sqlite3
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk

# Đọc dữ liệu từ SQLite
def load_product_data_from_db(db_file='products.db'):
    products = {}
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    try:
        c.execute("SELECT barcode, name, price FROM products")
        for barcode, name, price in c.fetchall():
            products[barcode.strip()] = {'name': name.strip(), 'price': int(price)}
    except sqlite3.Error as e:
        print("❌ Lỗi khi đọc DB:", e)
    finally:
        conn.close()
    return products

cooldown = 3
cart = {}
last_scanned_time = {}
product_data = load_product_data_from_db()
cap = cv2.VideoCapture(0)

# Gửi hóa đơn về web
def send_receipt_to_web():
    items, total = [], 0
    for item in cart.values():
        total += item['price'] * item['quantity']
        items.append({
            "name": item['name'],
            "price": item['price'],
            "quantity": item['quantity']
        })
    try:
        requests.post("http://127.0.0.1:5000/update_receipt", json={"items": items, "total": total})
    except:
        pass

# Cập nhật giao diện
def update_receipt():
    total = 0
    for row in tree.get_children():
        tree.delete(row)
    for item in cart.values():
        line_total = item['price'] * item['quantity']
        tree.insert('', tk.END, values=(
            f"{item['name']} (x{item['quantity']})",
            f"{item['price']:,}",
            item['quantity'],
            f"{line_total:,}"
        ))
        total += line_total
    total_label.config(text=f"Tổng cộng: {total:,} VND")
    count_label.config(text=f"Số món: {len(cart)}")
    send_receipt_to_web()

def remove_item():
    selected = tree.selection()
    if selected:
        name_raw = tree.item(selected[0])['values'][0]
        name = name_raw.split(' (x')[0]
        for barcode, item in list(cart.items()):
            if item['name'] == name:
                del cart[barcode]
                break
        update_receipt()

def clear_cart():
    if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ giỏ hàng không?"):
        cart.clear()
        update_receipt()
        status_label.config(text="🗑️ Giỏ hàng đã được xóa toàn bộ", foreground="red")

def edit_quantity():
    selected = tree.selection()
    if selected:
        name_raw = tree.item(selected[0])['values'][0]
        name = name_raw.split(' (x')[0]
        for barcode, item in cart.items():
            if item['name'] == name:
                qty = simpledialog.askinteger("Sửa số lượng", f"Số lượng mới cho {name}:", initialvalue=item['quantity'], minvalue=1)
                if qty is not None:
                    cart[barcode]['quantity'] = qty
                    update_receipt()
                break

def save_receipt():
    if cart:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"receipt_{now}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("======= HÓA ĐƠN =======\n")
            total = 0
            for item in cart.values():
                line_total = item['price'] * item['quantity']
                f.write(f"{item['name']:<25} {item['price']:>10,} x {item['quantity']:>2} = {line_total:,}\n")
                total += line_total
            f.write(f"-----------------------------\nTỔNG: {total:,} VND\n")
        print(f"📝 Hóa đơn đã lưu: {filename}")
        status_label.config(text=f"💾 Đã lưu hóa đơn: {filename}", foreground="blue")

# Giao diện Tkinter
root = tk.Tk()
root.title("Quét mã vạch & Hóa đơn")
root.geometry("1100x640")
style = ttk.Style()
style.configure("Treeview", rowheight=28)

# Left: Camera
frame_left = ttk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)
tk.Label(frame_left, text="📷 Camera", font=("Arial", 12, "bold")).pack()
video_label = ttk.Label(frame_left)
video_label.pack()

# Right: Hóa đơn
frame_right = ttk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
tk.Label(frame_right, text="🧾 HÓA ĐƠN MUA HÀNG", font=("Arial", 14, "bold")).pack(pady=(0, 5))

columns = ("Tên (xSố lượng)", "Giá", "Số lượng", "Tạm tính")
tree_frame = ttk.Frame(frame_right)
tree_frame.pack()

tree_scroll = ttk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15, yscrollcommand=tree_scroll.set)
tree_scroll.config(command=tree.yview)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER)
tree.pack()

count_label = ttk.Label(frame_right, text="Số món: 0", font=("Arial", 12))
count_label.pack()

total_label = ttk.Label(frame_right, text="Tổng cộng: 0 VND", font=("Arial", 14, "bold"))
total_label.pack()

btn_frame = ttk.Frame(frame_right)
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="💾 Lưu Hóa Đơn", command=save_receipt).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="🗑️ Xóa Món", command=remove_item).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="✏️ Sửa SL", command=edit_quantity).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="🧹 Xóa toàn bộ", command=clear_cart).pack(side=tk.LEFT, padx=5)

status_label = ttk.Label(root, text="", font=("Arial", 11), foreground="green")
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Cập nhật camera
def update_camera():
    ret, frame = cap.read()
    if ret:
        for barcode in decode(frame):
            x, y, w, h = barcode.rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            data = barcode.data.decode("utf-8")
            now = time.time()
            if now - last_scanned_time.get(data, 0) < cooldown:
                continue
            last_scanned_time[data] = now
            if data in product_data:
                p = product_data[data]
                if data not in cart:
                    cart[data] = {'name': p['name'], 'price': p['price'], 'quantity': 1}
                else:
                    cart[data]['quantity'] += 1
                update_receipt()
                text = f"{p['name']} - {p['price']} VND"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                status_label.config(text=f"✅ Đã thêm: {p['name']}", foreground="green")
            else:
                status_label.config(text="❌ Mã vạch không có trong CSDL", foreground="red")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb).resize((500, 380))  # Resize preview
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    root.after(10, update_camera)

update_camera()
root.mainloop()
cap.release()
cv2.destroyAllWindows()
