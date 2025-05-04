from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dữ liệu hóa đơn sẽ lưu tạm ở đây (giống như "bộ nhớ")
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

if __name__ == '__main__':
    app.run(debug=True)
