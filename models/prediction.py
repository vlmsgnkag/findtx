import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
import math

# Huấn luyện mô hình
def prepare_data():
    history_data = [
    (["Tài", "Xỉu", "Tài", "Tài", "Xỉu"], "Tài"),
    (["Xỉu", "Tài", "Xỉu", "Xỉu", "Tài"], "Xỉu"),
    (["Tài", "Tài", "Xỉu", "Xỉu", "Tài"], "Tài"),
    (["Xỉu", "Xỉu", "Tài", "Tài", "Xỉu"], "Xỉu"),
    (["Tài", "Tài", "Tài", "Xỉu", "Xỉu"], "Tài"),
    (["Xỉu", "Xỉu", "Xỉu", "Tài", "Tài"], "Xỉu"),
    
    # Các mẫu cầu phức tạp hơn
    (["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"], "Tài"),  # Cầu Xen Kẽ
    (["Tài", "Tài", "Xỉu", "Xỉu", "Tài", "Tài"], "Xỉu"),  # Cầu Lặp Kép
    (["Xỉu", "Tài", "Xỉu", "Tài", "Xỉu", "Tài"], "Xỉu"),  # Cầu Chữ U
    (["Tài", "Tài", "Tài", "Xỉu", "Xỉu", "Tài"], "Tài"),  # Cầu Bất Đối Xứng
    (["Tài", "Tài", "Tài", "Xỉu", "Xỉu", "Xỉu"], "Tài"),  # Cầu Bệt Dài
    (["Xỉu", "Xỉu", "Tài", "Tài", "Tài", "Xỉu"], "Tài"),  # Cầu Chu Kỳ Bất Đối Xứng
    (["Tài", "Xỉu", "Xỉu", "Tài", "Tài", "Xỉu"], "Tài"),  # Cầu Đảo
    (["Tài", "Xỉu", "Tài", "Xỉu", "Xỉu", "Tài", "Tài"], "Xỉu"),  # Cầu Chu Kỳ Biến Thiên

    # Các cầu mới từ patterns
    (["Tài", "Tài", "Tài", "Tài"], "Tài"),  # Cầu Bệt
    (["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"], "Tài"),  # Cầu Chéo
    (["Tài", "Xỉu", "Tài"], "Xỉu"),  # Cầu 1-2-3
    (["Xỉu", "Tài", "Xỉu"], "Tài"),  # Cầu 3-2-1
    (["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"], "Xỉu"),  # Cầu Chu Kỳ Lặp Lại
    (["Tài", "Tài", "Xỉu", "Xỉu", "Tài"], "Xỉu"),  # Cầu Thoái Lùi
    (["Tài", "Tài", "Xỉu", "Xỉu", "Xỉu", "Tài"], "Xỉu"),  # Cầu giảm dần
    (["Tài", "Xỉu", "Xỉu", "Tài", "Xỉu", "Tài"], "Xỉu"),  # Cầu chu kỳ dài
    (["Tài", "Tài", "Tài", "Xỉu", "Xỉu", "Xỉu"], "Tài"),  # Cầu Tài Bệt
    (["Tài", "Xỉu", "Tài", "Tài", "Xỉu"], "Xỉu"),  # Cầu xen dài
    (["Xỉu", "Xỉu", "Xỉu", "Tài", "Tài", "Tài"], "Xỉu"),  # Cầu Xỉu Bệt
    (["Xỉu", "Xỉu", "Tài", "Tài", "Tài", "Xỉu"], "Tài"), # Cầu đối xứng
    (["Tài", "Xỉu", "Xỉu", "Xỉu", "Tài"], "Tài"),  # Cầu Tài-Xỉu Tăng Dần
        # Thêm dữ liệu mẫu của bạn ở đây
    ]
    histories = [" ".join(h[0]) for h in history_data]
    targets = [h[1] for h in history_data]
    return histories, targets

def train_models():
    histories, targets = prepare_data()
    label_encoder = LabelEncoder()
    targets = label_encoder.fit_transform(targets)
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(histories)
    
    models = {}
    models["logistic_regression"] = LogisticRegression()
    models["logistic_regression"].fit(X, targets)
    
    models["random_forest"] = RandomForestClassifier(n_estimators=100, random_state=42)
    models["random_forest"].fit(X, targets)
    
    xgb_model = xgb.XGBClassifier(n_estimators=100)
    xgb_model.fit(X, targets)
    models["xgboost"] = xgb_model

    return models, vectorizer, label_encoder

def predict_with_models(models, vectorizer, label_encoder, history):
    history_str = " ".join(history)
    X = vectorizer.transform([history_str])
    
    predictions = {}

    # Logistic Regression
    predictions["logistic_regression"] = models["logistic_regression"].predict(X)[0]
    
    # Random Forest
    predictions["random_forest"] = models["random_forest"].predict(X)[0]
    
    # XGBoost
    predictions["xgboost"] = models["xgboost"].predict(X)[0]
    
    for model in predictions:
        predictions[model] = label_encoder.inverse_transform([predictions[model]])[0]
    
    return predictions

def detect_pattern(history):
    patterns = [
{"name": "Cầu Bệt (4 kết quả giống nhau)", 
         "rule": lambda h: len(h) >= 4 and all(x == h[-1] for x in h[-4:]), 
         "confidence": 0.99},
        {"name": "Cầu Siêu Bệt (7 kết quả giống nhau trở lên)", 
         "rule": lambda h: len(h) >= 7 and all(x == h[-1] for x in h[-7:]), 
         "confidence": 0.999},
        {"name": "Cầu Xen Kẽ (Tài-Xỉu-Tài-Xỉu...)", 
         "rule": lambda h: len(h) >= 6 and all(h[i] != h[i+1] for i in range(len(h) - 1)), 
         "confidence": 0.98},
        {"name": "Cầu 1-2 (Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 3 and h[-3:] == ["Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.96},
        {"name": "Cầu 3-2 (Tài-Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.97},
        {"name": "Cầu 1-1 (Tài-Xỉu hoặc Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 2 and h[-2:] in [["Tài", "Xỉu"], ["Xỉu", "Tài"]], 
         "confidence": 0.98},
        {"name": "Cầu 1-2-3 (Tài-Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 5 and h[-5:] == ["Tài", "Xỉu", "Tài"], 
         "confidence": 0.93},
         {"name": "Cầu 3-2-1 (Xỉu-Tài-Xỉu)", 
          "rule": lambda h: len(h) >= 5 and h[-5:] == ["Xỉu", "Tài", "Xỉu"],
          "confidence": 0.94},
        {"name": "Cầu Bệt Tăng Dần (Tài-Tài-Tài-Tài)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Tài", "Tài", "Tài"], 
         "confidence": 0.98},
        {"name": "Cầu 3-2 Tài-Xỉu (Tài-Tài-Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 5 and h[-5:] == ["Tài", "Tài", "Tài", "Xỉu", "Xỉu"],
         "confidence": 0.97},
        {"name": "Cầu Chéo (Tài-Xỉu-Tài-Xỉu-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu"] * 3, 
         "confidence": 0.95},
        {"name": "Cầu Chéo Lặp Lại", 
         "rule": lambda h: len(h) >= 8 and h[-8:] == ["Tài", "Xỉu"] * 4, 
         "confidence": 0.96},
        {"name": "Cầu 2-1 (Xỉu-Tài-Tài)", 
         "rule": lambda h: len(h) >= 3 and h[-3:] == ["Xỉu", "Tài", "Tài"], 
         "confidence": 0.96},
        {"name": "Cầu Lặp Dài", 
         "rule": lambda h: len(h) >= 6 and h[-6:-3] == h[-3:], 
         "confidence": 0.99},
        {"name": "Cầu Đảo (Tài-Xỉu-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Xỉu", "Tài", "Xỉu"], 
         "confidence": 0.94},

        # Các cầu mới thêm vào
        {"name": "Cầu Nhịp Dài", 
         "rule": lambda h: len(h) >= 10 and h[-10:-5] == h[-5:], 
         "confidence": 0.98},
        {"name": "Cầu Xen Nhiễu Loạn", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu", "Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.95},
        {"name": "Cầu Tăng/Thoái Lùi", 
         "rule": lambda h: len(h) >= 5 and h[-5:] in [["Tài", "Xỉu", "Xỉu", "Tài", "Tài"], ["Xỉu", "Tài", "Tài", "Xỉu", "Xỉu"]], 
         "confidence": 0.97},
        {"name": "Cầu Chu Kỳ Lặp Lại", 
         "rule": lambda h: len(h) >= 6 and h[-6:-3] == h[-3:], 
         "confidence": 0.97},
        {"name": "Cầu Lặp Lại", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == h[-8:-4], 
         "confidence": 0.96},
        {"name": "Cầu Xen Tăng Dần", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"], 
         "confidence": 0.95},
        {"name": "Cầu Chu Kỳ Biến Thiên (Tài-Xỉu-Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Xỉu", "Xỉu", "Tài"], 
         "confidence": 0.93},
        {"name": "Cầu Tài-Xỉu Tăng Dần (Tài-Xỉu-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Xỉu", "Xỉu", "Xỉu"], 
         "confidence": 0.96},
        {"name": "Cầu Tài-Xỉu Đều (Tài-Xỉu-Tài-Xỉu-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu"] * 3, 
         "confidence": 0.97},
        {"name": "Cầu Tăng Dần (Tài-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 3 and h[-3:] == ["Tài", "Tài", "Xỉu"], 
         "confidence": 0.95},
        {"name": "Cầu Tròn (Tài-Xỉu-Tài-Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 5 and h[-5:] == ["Tài", "Xỉu", "Tài", "Xỉu", "Tài"], 
         "confidence": 0.94},
        {"name": "Cầu Đối Xứng (Tài-Xỉu-Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Xỉu", "Xỉu", "Tài"],
         "confidence": 0.99},
        {"name": "Cầu Lặp Kép (Tài-Tài-Xỉu-Xỉu-Tài-Tài)",
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Tài", "Xỉu", "Xỉu", "Tài", "Tài"], 
         "confidence": 0.99},
        {"name": "Cầu Xen Lặp Dài (Tài-Xỉu-Tài-Xỉu-Tài-Tài)", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Tài"], 
         "confidence": 0.98},
        {"name": "Cầu Chuỗi Liên Tiếp (Tài-Xỉu-Tài-Xỉu-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 6 and h[-6:] == ["Tài", "Xỉu"] * 3, 
         "confidence": 0.98},
        {"name": "Cầu Liên Kết (Tài-Tài-Xỉu-Tài-Xỉu)", 
         "rule": lambda h: len(h) >= 5 and h[-5:] == ["Tài", "Tài", "Xỉu", "Tài", "Xỉu"], 
         "confidence": 0.95},
        {"name": "Cầu Thoái Lùi (Tài-Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.94},
        {"name": "Cầu Lặp Tăng Dần (Tài-Tài-Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 5 and h[-5:] == ["Tài", "Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.96},
        {"name": "Cầu Lặp Kép (Tài-Tài-Xỉu-Xỉu)", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.92},
        {"name": "Cầu Chữ U (Tài-Xỉu-Tài)", 
         "rule": lambda h: len(h) >= 3 and h[-3:] == ["Tài", "Xỉu", "Tài"], 
         "confidence": 0.93},
        {"name": "Cầu Xen Dài (Tài-Xỉu lặp lại nhiều lần)", 
         "rule": lambda h: len(h) >= 8 and h[-8:] == ["Tài", "Xỉu"] * 4, 
         "confidence": 0.92},
        {"name": "Cầu giảm dần", 
         "rule": lambda h: len(h) >= 4 and h[-4:] == ["Tài", "Tài", "Xỉu", "Xỉu"], 
         "confidence": 0.93},
        # Thêm các mẫu cầu khác nếu cần
    ]
    
    possible_patterns = [p for p in patterns if p["rule"](history)]
    
    if not possible_patterns:
        return "Không có cầu rõ ràng", 0.85
    
    best_pattern = max(possible_patterns, key=lambda p: p["confidence"])
    return best_pattern["name"], best_pattern["confidence"]

def weighted_probability(history):
    count_tai = 0
    count_xiu = 0
    total_weight = 0

    # Tính toán trọng số mũ cho mỗi kết quả trong lịch sử
    for i, result in enumerate(reversed(history)):
        weight = math.exp(i / 0.3)
        if result == "Tài":
            count_tai += weight
        elif result == "Xỉu":
            count_xiu += weight
        total_weight += weight

    # Nếu tổng trọng số bằng 0, trả về xác suất mặc định (50% cho cả Tài và Xỉu)
    if total_weight == 0:
        return 0.5, 0.5  # Xác suất mặc định khi không có trọng số

    prob_tai = count_tai / total_weight
    prob_xiu = count_xiu / total_weight
    return prob_tai, prob_xiu

# Hàm này là nơi kết hợp các dự đoán từ các mô hình
def ensemble_prediction(history, models, vectorizer, label_encoder):
    predictions = predict_with_models(models, vectorizer, label_encoder, history)
    
    # Dự đoán từ phân tích mẫu cầu
    pattern, pattern_confidence = detect_pattern(history)

    # Dự đoán từ trọng số mũ
    prob_tai, prob_xiu = weighted_probability(history)

    # Kết hợp các phương pháp để đưa ra dự đoán cuối cùng
    final_predictions = {}
    for model_name, pred in predictions.items():
        final_predictions[model_name] = pred

    final_prediction = max(final_predictions, key=lambda x: final_predictions[x])

    if pattern_confidence > max(prob_tai, prob_xiu):
        return pattern, pattern_confidence * 100
    else:
        if final_prediction == "Tài":
            return "Tài", prob_tai * 100
        else:
            return "Xỉu", prob_xiu * 100
