from flask import Flask, render_template, request
from models.prediction import train_models, ensemble_prediction, detect_pattern  # Import mô hình từ models/prediction.py

app = Flask(__name__)

# Biến toàn cục để lưu trữ lịch sử kết quả
history = []  # Danh sách chứa lịch sử kết quả nhập vào từ người dùng

@app.route('/', methods=['GET', 'POST'])
def index():
    global history  # Đảm bảo sử dụng biến toàn cục history

    prediction = None

    if request.method == 'POST':
        # Kiểm tra và lấy 6 kết quả nhập từ form (6 kết quả ban đầu)
        for i in range(1, 7):
            result = request.form.get(f'result_{i}')
            if result:
                # Kiểm tra nếu result là chuỗi hợp lệ
                if isinstance(result, str):
                    history.insert(0, result.strip().capitalize())  # Chèn kết quả vào đầu danh sách

        # Giới hạn chỉ có 6 kết quả trong lịch sử
        if len(history) > 6:
            history = history[:6]  # Giới hạn chỉ giữ lại 6 kết quả mới nhất

        # Nếu người dùng nhập thêm kết quả mới
        if 'result_new' in request.form:
            result_new = request.form.get('result_new').strip().capitalize()
            if isinstance(result_new, str):
                history.insert(0, result_new)  # Chèn kết quả mới vào đầu danh sách

        # Giới hạn lại chỉ có 6 kết quả sau khi nhập thêm
        if len(history) > 6:
            history = history[:6]  # Chỉ giữ lại 6 kết quả mới nhất

        # Tạo mô hình và thực hiện dự đoán
        models, vectorizer, label_encoder = train_models()
        next_prediction, confidence = ensemble_prediction(history, models, vectorizer, label_encoder)
        pattern, pattern_confidence = detect_pattern(history)
        
        prediction = {
            'next_prediction': next_prediction,
            'confidence': confidence,
            'pattern': pattern,
            'pattern_confidence': pattern_confidence,
            'history': history
        }

    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
