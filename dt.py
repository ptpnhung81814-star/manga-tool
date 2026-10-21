import os
import zipfile
import io
from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Thư mục lưu trữ font tùy chỉnh
UPLOAD_FOLDER = 'custom_fonts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Giao diện HTML/CSS/JS tích hợp cho Mobile và PC
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comic Typesetting Tool - Đa Nền Tảng</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #007bff; text-align: center; font-size: 24px; }
        .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 6px; background: #fafafa; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        input[type="file"], select { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
        button { background: #28a745; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background: #218838; }
        .result-box { margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Comic Typesetting & Balloon Tool</h1>
        
        <!-- Mục 1: Quản lý Font (Tối đa 10 font) -->
        <div class="section">
            <h3>1. Thêm Font Chữ Tùy Chỉnh (Tối đa 10 file .ttf / .otf)</h3>
            <form action="/upload_fonts" method="POST" enctype="multipart/form-data">
                <input type="file" name="fonts" multiple accept=".ttf,.otf">
                <button type="submit">Tải Lên Font</button>
            </form>
        </div>

        <!-- Mục 2: Xử lý Bóng Thoại & Text -->
        <div class="section">
            <h3>2. Xử Lý Ảnh & Căn Chỉnh Bóng Thoại</h3>
            <form action="/process" method="POST" enctype="multipart/form-data">
                <label>Chọn ảnh truyện tranh:</label>
                <input type="file" name="image" accept="image/*" required>
                
                <label>Loại bóng thoại phát hiện:</label>
                <select name="balloon_type">
                    <option value="normal">Bóng thoại thường (Tròn/Oval)</option>
                    <option value="square">Bóng thoại vuông (Suy nghĩ/Lời dẫn)</option>
                    <option value="shout">Bóng thoại la hét (Gai góc/Sắc nhọn)</option>
                    <option value="tremble">Bóng thoại run rẩy (Nét gợn sóng)</option>
                    <option value="open">Bóng thoại bị hở (Không viền kín)</option>
                </select>

                <label>Nội dung Text:</label>
                <textarea name="text_content" rows="3" style="width:100%; padding:8px;" placeholder="Nhập hội thoại vào đây..."></textarea>

                <button type="submit" style="margin-top: 10px;">Xử Lý & Tải về ZIP</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload_fonts', methods=['POST'])
def upload_fonts():
    files = request.files.getlist('fonts')
    if len(files) > 10:
        return "Lỗi: Bạn chỉ được tải lên tối đa 10 font chữ mỗi lần!", 400
    
    count = 0
    for file in files:
        if file and file.filename.endswith(('.ttf', '.otf')):
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            count += 1
    return f"Đã tải lên thành công {count} font chữ! <a href='/'>Quay lại</a>"

@app.route('/process', methods=['POST'])
def process():
    file = request.files['image']
    balloon_type = request.form['balloon_type']
    text_content = request.form['text_content']
    
    # Đọc ảnh gốc
    img = Image.open(file.stream).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # --- ĐỀ XUẤT THÔNG SỐ DỰA TRÊN LOẠI BÓNG THOẠI ---
    # (Hệ thống tự động chọn font, cỡ chữ và kiểu căn chỉnh phù hợp)
    font_size = 20
    align_center = True
    
    if balloon_type == 'normal':
        font_size = 18
    elif balloon_type == 'square':
        font_size = 16
    elif balloon_type == 'shout':
        font_size = 22  # La hét cần chữ to, mạnh mẽ
    elif balloon_type == 'tremble':
        font_size = 19
    elif balloon_type == 'open':
        font_size = 18

    # Sử dụng font mặc định hoặc font tải lên đầu tiên nếu có
    font_path = os.path.join("arial.ttf")
    custom_fonts = os.listdir(UPLOAD_FOLDER)
    if custom_fonts:
        font_path = os.path.join(UPLOAD_FOLDER, custom_fonts[0])
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # --- TỰ ĐỘNG CĂN CHỈNH VÀ VẼ TEXT VÀO GIỮA ẢNH/BÓNG THOẠI ---
    width, height = img.size
    
    # Chia dòng text nếu quá dài
    lines = text_content.split('\n')
    
    # Tính toán vị trí để căn giữa tuyệt đối
    total_text_height = len(lines) * (font_size + 6)
    start_y = (height - total_text_height) / 2

    for i, line in enumerate(lines):
        # Đo chiều rộng text để căn giữa ngang
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        start_x = (width - text_width) / 2
        
        draw.text((start_x, start_y + i * (font_size + 6)), line, fill="black", font=font)

    # Đóng gói kết quả vào file ZIP để chia sẻ
    output_img_io = io.BytesIO()
    img.convert("RGB").save(output_img_io, 'JPEG')
    output_img_io.seek(0)

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("typeset_result.jpg", output_img_io.getvalue())
        # Đính kèm file cấu hình gợi ý dạng text
        suggestion_text = f"""--- GỢI Ý TYPESETTING ---
Loại bóng thoại: {balloon_type}
Đề xuất Cỡ chữ (Font Size): {font_size}px
Căn lề: Căn giữa (Center Aligned)
Ghi chú: Phù hợp tiêu chuẩn đọc truyện tranh.
"""
        zip_file.writestr("suggestions.txt", suggestion_text)
    
    zip_io.seek(0)
    
    return send_file(
        zip_io,
        mimetype='application/zip',
        as_attachment=True,
        download_name='comic_typeset_package.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
