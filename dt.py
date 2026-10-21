import os
import zipfile
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Cấu hình giao diện trang web
st.set_page_config(page_title="Comic Typeset & Balloon Tool", page_icon="🎨", layout="centered")

UPLOAD_FOLDER = 'custom_fonts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("🎨 Comic Typeset & Balloon Tool")
st.write("Công cụ căn chỉnh text, đề xuất font/cỡ chữ cho từng loại bóng thoại và xuất file ZIP đa nền tảng (PC & Điện thoại).")

# --- MỤC 1: QUẢN LÝ FONT CHỮ ---
st.header("1. Quản lý Font Chữ")
uploaded_fonts = st.file_uploader(
    "Tải lên font chữ tùy chỉnh (Chọn tối đa 10 file .ttf hoặc .otf)", 
    type=["ttf", "otf"], 
    accept_multiple_files=True
)

if uploaded_fonts:
    if len(uploaded_fonts) > 10:
        st.error("❌ Bạn chỉ được tải lên tối đa 10 font chữ mỗi lần!")
    else:
        saved_count = 0
        for f in uploaded_fonts:
            with open(os.path.join(UPLOAD_FOLDER, f.name), "wb") as out:
                out.write(f.getbuffer())
            saved_count += 1
        st.success(f"✅ Đã tải lên thành công {saved_count} font chữ!")

# --- MỤC 2: XỬ LÝ ẢNH & BÓNG THOẠI ---
st.header("2. Xử Lý Bóng Thoại & Tạo File ZIP")

with st.form("typeset_form"):
    uploaded_image = st.file_uploader("Tải lên ảnh truyện tranh / bóng thoại", type=["jpg", "jpeg", "png"])
    
    balloon_type = st.selectbox(
        "Chọn loại bóng thoại:",
        options=["normal", "square", "shout", "tremble", "open"],
        format_func=lambda x: {
            "normal": "Bóng thoại thường (Tròn / Oval)",
            "square": "Bóng thoại vuông (Suy nghĩ / Lời dẫn)",
            "shout": "Bóng thoại la hét (Gai góc / Nhọn)",
            "tremble": "Bóng thoại run rẩy (Nét gợn sóng)",
            "open": "Bóng thoại hở (Không kín viền)"
        }[x]
    )
    
    text_content = st.text_area("Nhập nội dung hội thoại (mỗi dòng là một dòng chữ):", placeholder="Ví dụ:\nXin chào!\nBạn đang làm gì thế?")
    
    submitted = st.form_submit_button("Xử Lý & Đóng Gói ZIP")

if submitted and uploaded_image is not None:
    # Mở ảnh
    img = Image.open(uploaded_image).convert("RGBA")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Đề xuất thông số dựa trên loại bóng thoại
    font_size = int(height * 0.05)
    rec_style = "Mặc định"
    
    if balloon_type == 'shout':
        font_size = int(height * 0.07)
        rec_style = "Font in hoa, nét dày, góc cạnh"
    elif balloon_type == 'square':
        font_size = int(height * 0.04)
        rec_style = "Font nghiêm túc, ô vuông"

    # Chọn font (lấy font tải lên đầu tiên hoặc mặc định)
    custom_fonts = os.listdir(UPLOAD_FOLDER)
    if custom_fonts:
        font_path = os.path.join(UPLOAD_FOLDER, custom_fonts[0])
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    # Căn giữa text vào ảnh/bóng thoại
    lines = text_content.split('\n')
    line_height = font_size * 1.3
    total_text_height = len(lines) * line_height
    start_y = (height - total_text_height) / 2

    for i, line in enumerate(lines):
        bbox = font.getbbox(line) if hasattr(font, 'getbbox') else (0, 0, 100, 20)
        text_width = bbox[2] - bbox[0]
        start_x = (width - text_width) / 2
        
        # Viền chữ trắng để nổi bật
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            draw.text((start_x + dx, start_y + i * line_height + dy), line, fill="white", font=font)
        # Chữ đen chính
        draw.text((start_x, start_y + i * line_height), line, fill="black", font=font)

    # Xuất ảnh ra bộ nhớ đệm
    img_io = io.BytesIO()
    img.convert("RGB").save(img_io, format='JPEG')
    img_io.seek(0)

    # File gợi ý thông số
    suggestion_text = f"""=== ĐỀ XUẤT CHO BÓNG THOẠI ===
- Loại bóng thoại: {balloon_type}
- Cỡ chữ đề xuất: {font_size}px
- Phong cách font gợi ý: {rec_style}
- Trạng thái: Đã căn giữa tuyệt đối
"""

    # Tạo file ZIP
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("typeset_ket_qua.jpg", img_io.getvalue())
        zipf.writestr("de_xuat_thong_so.txt", suggestion_text)
    zip_io.seek(0)

    st.success("🎉 Xử lý thành công! Nhấn vào nút dưới để tải file ZIP về máy/điện thoại:")
    st.download_button(
        label="📥 Tải Xuống File ZIP (.zip)",
        data=zip_io,
        file_name="comic_typeset_package.zip",
        mime="application/zip"
    )
elif submitted and uploaded_image is None:
    st.warning("⚠️ Vui lòng tải lên một bức ảnh trước khi xử lý!")
