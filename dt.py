<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Công cụ căn chỉnh Text vào bóng thoại</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            width: 400px;
        }
        h2 { text-align: center; color: #333; }
        label { display: block; margin-top: 10px; font-weight: bold; font-size: 14px; }
        textarea, input, select {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .preview-area {
            margin-top: 20px;
            height: 250px;
            border: 2px dashed #007bff;
            border-radius: 50%; /* Giả lập bóng thoại tròn/oval */
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            background-color: #fff;
            position: relative;
            overflow: hidden;
        }
        #outputText {
            margin: 0;
            word-break: break-word;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>Căn Giữa Bóng Thoại</h2>
    
    <label for="inputText">Nhập nội dung thoại:</label>
    <textarea id="inputText" rows="3" placeholder="Nhập chữ vào đây...">Xin chào! Đây là đoạn hội thoại mẫu.</textarea>
    
    <label for="fontFamily">Font chữ:</label>
    <select id="fontFamily" onchange="updateStyle()">
        <option value="Arial">Arial</option>
        <option value="Comic Sans MS">Comic Sans (Truyện tranh)</option>
        <option value="Times New Roman">Times New Roman</option>
        <option value="Courier New">Courier New</option>
    </select>

    <label for="fontSize">Cỡ chữ (px):</label>
    <input type="number" id="fontSize" value="16" min="10" max="40" oninput="updateStyle()">

    <label for="textAlign">Căn lề chữ:</label>
    <select id="textAlign" onchange="updateStyle()">
        <option value="center">Giữa (Center)</option>
        <option value="left">Trái (Left)</option>
        <option value="right">Phải (Right)</option>
    </select>

    <label>Khu vực mô phỏng bóng thoại:</label>
    <div class="preview-area" id="bubblePreview">
        <p id="outputText">Xin chào! Đây là đoạn hội thoại mẫu.</p>
    </div>
</div>

<script>
    const input = document.getElementById('inputText');
    const output = document.getElementById('outputText');
    const fontSelect = document.getElementById('fontFamily');
    const sizeInput = document.getElementById('fontSize');
    const alignSelect = document.getElementById('textAlign');

    function updateStyle() {
        // Thay thế ngắt dòng bằng thẻ <br> để giữ nguyên format xuống dòng
        output.innerHTML = input.value.replace(/\n/g, '<br>');
        output.style.fontFamily = fontSelect.value;
        output.style.fontSize = sizeInput.value + 'px';
        output.style.textAlign = alignSelect.value;
    }

    input.addEventListener('input', updateStyle);
    updateStyle();
</script>

</body>
</html>
