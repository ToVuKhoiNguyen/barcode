import cv2
from pyzbar.pyzbar import decode

# Mở camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Chuyển ảnh về màu xám để giảm nhiễu và cải thiện độ tương phản
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Áp dụng GaussianBlur để giảm nhiễu trong ảnh, giúp cải thiện quá trình phát hiện
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Giải mã các mã vạch từ ảnh đã xử lý
    barcodes = decode(blurred_frame)

    # Nếu có mã vạch, xử lý
    if len(barcodes) > 0:
        for barcode in barcodes:
            # Lấy dữ liệu mã vạch và giải mã
            barcode_data = barcode.data.decode("utf-8")
            print(f"Mã vạch: {barcode_data}")  # In ra mã vạch đã giải mã

            # Vẽ hình chữ nhật quanh mã vạch
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Hiển thị thông tin mã vạch trên hình ảnh
            text = barcode_data
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y - 10
            if text_y < 10:
                text_y = y + h + 20
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Hiển thị hình ảnh với mã vạch và thông tin
    cv2.imshow("Barcode Scanner", frame)

    # Thoát khi nhấn phím 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
