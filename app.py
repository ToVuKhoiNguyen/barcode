from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF
import io
from datetime import datetime

app = Flask(__name__)

# Dữ liệu hóa đơn tạm thời
receipt_data = {
    "store": "IOT CHALLENGE",
    "items": [],
    "total": 0,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

@app.route('/')
def index():
    return render_template('receipt.html', receipt=receipt_data)

@app.route('/update_receipt', methods=['GET'])
def update_receipt():
    return jsonify(receipt_data)

@app.route('/update_receipt', methods=['POST'])
def post_update_receipt():
    global receipt_data
    receipt_data = request.json
    receipt_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"status": "updated"})

@app.route('/download_pdf')
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=receipt_data["store"], ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Thời gian: {receipt_data['timestamp']}", ln=True, align='C')
    pdf.ln(10)

    for item in receipt_data["items"]:
        line = f"{item['name']} (x{item['quantity']}) - {item['price'] * item['quantity']} VND"
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.ln(10)
    pdf.set_text_color(220, 50, 50)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TỔNG: {receipt_data['total']} VND", ln=True, align='R')

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    filename = f"hoadon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
