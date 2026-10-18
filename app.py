import os
from flask import Flask, request, jsonify
import qrcode
from io import BytesIO
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)

UPI_ID = "SPICED84789572682300267@yesbankltd"
SHOP_NAME = "Global Cyber Hub"

HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Cyber Hub</title>
<style>body{font-family:Arial;background:#f0f2f5;padding:15px}.card{background:white;max-width:450px;margin:auto;padding:20px;border-radius:15px}input,select{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}.btn{background:#1a73e8;color:white;border:none;padding:14px;width:100%;border-radius:8px;font-size:16px}</style>
</head><body><div class="card">
<h2 style="text-align:center;color:#1a73e8">🖨️ Global Cyber Hub</h2>
<p style="text-align:center">BW: ₹2 / পেজ | Color: ₹10 / পেজ</p>
<label>ফাইল সিলেক্ট করো</label><input type="file" id="file">
<label>প্রিন্টের ধরন</label><select id="print_type"><option value="bw">Black & White - ₹2</option><option value="color">Color - ₹10</option></select>
<label>কত পেজ?</label><input type="number" id="pages" value="1">
<label>কত কপি?</label><input type="number" id="copies" value="1">
<button class="btn" onclick="calc()">দাম দেখো & QR বানাও</button>
<div id="price" style="text-align:center;font-weight:bold;margin:10px"></div>
<div id="qrBox" style="text-align:center;display:none"><img id="qrImg" style="width:200px"><p>QR স্ক্যান করে পেমেন্ট করো</p><button class="btn" style="background:#0d9b4a" onclick="doPrint()">পেমেন্ট করেছি, ফাইল পাঠাও</button></div>
<p id="msg" style="text-align:center"></p></div>
<script>
let f; document.getElementById('file').addEventListener('change', e=>{f=e.target.files[0]});
async function calc(){ if(!f){alert('আগে ফাইল দাও');return;} let fd=new FormData(); fd.append('copies',document.getElementById('copies').value); fd.append('pages',document.getElementById('pages').value); fd.append('print_type',document.getElementById('print_type').value); let r=await fetch('/calculate',{method:'POST',body:fd}); let d=await r.json(); document.getElementById('price').innerText='মোট দাম: ₹'+d.amount; document.getElementById('qrImg').src='data:image/png;base64,'+d.qr_code; document.getElementById('qrBox').style.display='block'; }
async function doPrint(){ let fd=new FormData(); fd.append('file',f); let r=await fetch('/process-print',{method:'POST',body:fd}); let d=await r.json(); document.getElementById('msg').innerText=d.message; }
</script></body></html>
"""

@app.route('/')
def index():
    return HTML

@app.route('/calculate', methods=['POST'])
def calculate():
    copies = int(request.form.get('copies', 1))
    ptype = request.form.get('print_type', 'bw')
    pages = int(request.form.get('pages', 1))
    rate = 2 if ptype == 'bw' else 10
    total = rate * pages * copies
    upi_url = f"upi://pay?pa={UPI_ID}&pn={SHOP_NAME}&am={total}&cu=INR"
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(upi_url); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({'amount': total, 'qr_code': qr_b64})

@app.route('/process-print', methods=['POST'])
def process_print():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join('uploads', filename))
    return jsonify({'message': 'ফাইল জমা হয়েছে! পেমেন্ট কনফার্ম হলে প্রিন্ট দেবো'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)