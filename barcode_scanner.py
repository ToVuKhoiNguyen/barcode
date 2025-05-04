import cv2
from pyzbar.pyzbar import decode

# Mở camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    barcodes = decode(frame)

    for barcode in barcodes:
        data = barcode.data.decode("utf-8")
        print(f" Mã vạch: {data}")

        # Vẽ khung quanh mã vạch
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Hiển thị nội dung mã vạch trên ảnh
        cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 0), 2)

    # Hiển thị cửa sổ camera
    cv2.imshow("Barcode Scanner", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
