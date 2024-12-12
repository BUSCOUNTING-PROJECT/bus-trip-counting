import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from python_files.python_1 import process_file1
from python_files.python_2 import process_file2

app = Flask(__name__)

# กำหนดที่เก็บไฟล์ที่อัปโหลด
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'py'}  # ตัวอย่างไฟล์ที่อนุญาต
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ฟังก์ชันตรวจสอบประเภทไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"resul t": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"result": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # เรียกใช้ฟังก์ชันจากไฟล์ Python ที่ผู้ใช้เลือก
        if 'scriptOption' in request.form:
            option = request.form['scriptOption']
            if option == "1":
                result = process_file1(filepath)  # Call the function from python_1.py
            elif option == "2":
                result = process_file2(filepath)  # Ensure this is implemented
            else:
                result = "Invalid option selected"
        
        return jsonify({"result": result})
    else:
        return jsonify({"result": "File type not allowed"})

if __name__ == "__main__":
    app.run(debug=True)
