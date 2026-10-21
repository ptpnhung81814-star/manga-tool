import os
import io
import zipfile
import requests
from bs4 import BeautifulSoup
from PIL import Image
import streamlit as st

# Thiết lập giao diện trang web
st.set_page_config(page_title="Manga Raw Downloader & Merger", page_icon="📚", layout="centered")

st.title("📚 Tool Tải & Cắt Ghép Raw Truyện Tranh")
st.write("Tự động tải, lọc bỏ ảnh quảng cáo rác, chỉnh kích thước và ghép truyện theo yêu cầu.")

# --- KHUNG NHẬP THÔNG TIN ---
with st.form("manga_form"):
    url_input = st.text_input("Đường dẫn (URL) chương truyện:", placeholder="https://trangtruyen.com/chapter-1")
    desired_width = st.slider("Chiều ngang mong muốn (Pixel):", min_value=400, max_value=2000, value=800, step=50)
    min_height_filter = st.number_input("Bỏ qua ảnh có chiều cao nhỏ hơn (Pixel) - Lọc quảng cáo:", value=150, step=10)
    max_page_height = st.slider("Chiều cao tối đa mỗi dải ảnh ghép (Pixel):", min_value=3000, max_value=30000, value=12000, step=1000)
    
    submitted = st.form_submit_button("🚀 Bắt đầu xử lý")

# --- XỬ LÝ KHI BẤM NÚT ---
if submitted:
    if not url_input.strip():
        st.error("⚠️ Vui lòng nhập URL của chương truyện!")
    else:
        with st.spinner("⏳ Đang tải và xử lý hình ảnh... Vui lòng chờ trong giây lát."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                response = requests.get(url_input, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                img_tags = soup.find_all('img')
                
                # Quét tất cả link ảnh trong trang
                image_urls = []
                for img in img_tags:
                    src = img.get('src') or img.get('data-src') or img.get('data-original') or img.get('data-lazy-src')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            from urllib.parse import urlparse
                            parsed_uri = urlparse(url_input)
                            src = f"{parsed_uri.scheme}://{parsed_uri.netloc}{src}"
                        
                        if src.startswith('http'):
                            image_urls.append(src)

                # Loại bỏ các link trùng lặp nhưng giữ nguyên thứ tự
                image_urls = list(dict.fromkeys(image_urls))

                if not image_urls:
                    st.error("❌ Không tìm thấy thẻ hình ảnh nào trên trang web này.")
                else:
                    # Lọc ảnh rác
                    valid_images = []
                    for url in image_urls:
                        try:
                            img_res = requests.get(url, headers=headers, timeout=8)
                            if img_res.status_code == 200:
                                img = Image.open(io.BytesIO(img_res.content))
                                w, h = img.size
                                if h >= min_height_filter and w >= 200:
                                    valid_images.append(img.convert("RGB"))
                        except:
                            continue

                    if not valid_images:
                        st.warning("⚠️ Không có ảnh nào vượt qua bộ lọc (Hãy thử giảm mức lọc chiều cao xuống).")
                    else:
                        st.info(f"✅ Đã tìm thấy và lọc được **{len(valid_images)}** ảnh truyện hợp lệ!")

                        # Resize ảnh về chiều ngang chuẩn
                        resized_images = []
                        for img in valid_images:
                            w, h = img.size
                            if w != desired_width:
                                new_height = int(desired_width * (h / w))
                                img = img.resize((desired_width, new_height), Image.Resampling.LANCZOS)
                            resized_images.append(img)

                        # Cắt ghép thành từng dải trang chuẩn
                        chunks = []
                        current_chunk = []
                        current_h = 0

                        for img in resized_images:
                            if current_h + img.height > max_page_height and current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = [img]
                                current_h = img.height
                            else:
                                current_chunk.append(img)
                                current_h += img.height
                        
                        if current_chunk:
                            chunks.append(current_chunk)

                        # --- TẠO FILE ZIP ĐỂ TẢI TẤT CẢ ---
                        zip_buffer = io.BytesIO()
                        processed_pages = []

                        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for idx, chunk in enumerate(chunks, 1):
                                total_h = sum(img.height for img in chunk)
                                combined_img = Image.new("RGB", (desired_width, total_h))
                                
                                y_offset = 0
                                for img in chunk:
                                    combined_img.paste(img, (0, y_offset))
                                    y_offset += img.height

                                # Chuyển ảnh thành dữ liệu byte
                                img_buf = io.BytesIO()
                                combined_img.save(img_buf, format="JPEG", quality=95)
                                byte_data = img_buf.getvalue()

                                # Thêm vào danh sách hiển thị
                                processed_pages.append((idx, desired_width, total_h, byte_data))

                                # Đưa ảnh vào file ZIP
                                file_name_in_zip = f"manga_page_{idx:02d}.jpg"
                                zip_file.writestr(file_name_in_zip, byte_data)

                        # NÚT TẢI TẤT CẢ (FILE ZIP)
                        st.subheader("🎉 Kết quả xử lý")
                        st.download_button(
                            label="📦 TẢI TẤT CẢ TRANG (FILE .ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="manga_chapter_full.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                        st.markdown("---")

                        # HIỂN THỊ TỪNG TRANG & NÚT TẢI TỪNG TRANG NẾU CẦN
                        for idx, width, height, byte_im in processed_pages:
                            st.write(f"**Trang {idx}** (Kích thước: {width}x{height}px)")
                            st.image(byte_im, use_container_width=True)
                            
                            st.download_button(
                                label=f"⬇️ Tải lẻ Trang {idx}",
                                data=byte_im,
                                file_name=f"manga_page_{idx:02d}.jpg",
                                mime="image/jpeg",
                                key=f"btn_{idx}"
                            )
                            st.markdown("---")

            except Exception as e:
                st.error(f"❌ Có lỗi xảy ra trong quá trình xử lý: {e}")
