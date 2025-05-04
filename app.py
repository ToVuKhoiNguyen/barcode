from flask import Flask, render_template, request, jsonify, send_file
from fpdf import FPDF
import io

app = Flask(__name__)

# Dữ liệu hóa đơn lưu tạm
receipt_data = {
    "items": [],
    "total": 0
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
    return jsonify({"status": "updated"})

@app.route('/download_pdf')
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="HÓA ĐƠN", ln=True, align='C')
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

    return send_file(buffer, as_attachment=True, download_name="hoadon.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
