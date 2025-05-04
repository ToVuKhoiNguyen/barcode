import cv2
import csv
import time
from pyzbar.pyzbar import decode
from datetime import datetime

# Đọc dữ liệu sản phẩm từ CSV
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

# Lưu hóa đơn vào file .txt
def save_invoice_to_txt(cart):
    with open("invoice.txt", "w", encoding="utf-8") as file:
        total = 0
        file.write("======== HÓA ĐƠN ========\n")
        file.write("{:<25} {:>10} {:>10}\n".format("Tên sản phẩm", "Giá", "Số lượng"))
        file.write("-" * 50 + "\n")
        for item in cart.values():
            line_total = item['price'] * item['quantity']
            file.write("{:<25} {:>10,} {:>10}\n".format(item['name'], item['price'], item['quantity']))
            total += line_total
        file.write("-" * 50 + "\n")
        file.write("{:<25} {:>10,} VND\n".format("TỔNG TIỀN", total))
        file.write("=========================\n")

# Quét barcode và xử lý
def scan_barcodes():
    cap = cv2.VideoCapture(0)
    cart = {}
    last_scanned_time = {}
    product_data = load_product_data_from_csv()

    cooldown = 3  # Giới hạn thời gian quét lại barcode

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

                # Hiển thị thông tin sản phẩm vừa quét
                text = f"{name} - {price} VND"
                (text_x, text_y) = (x + (w - len(text)) // 2, y - 10 if y > 20 else y + h + 30)
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                # Lưu hóa đơn vào file
                save_invoice_to_txt(cart)

        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Nhấn 'q' để thoát
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_barcodes()
