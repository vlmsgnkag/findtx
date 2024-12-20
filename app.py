import os
from flask import Flask, render_template, request, jsonify
from haha import simulate_games

# Khởi tạo Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        md5_hash = data.get('md5')
        num_games = int(data.get('num_games', 10000))

        if len(md5_hash) != 32 or not all(c in "0123456789abcdefABCDEF" for c in md5_hash):
            raise ValueError("MD5 không hợp lệ! MD5 phải có 32 ký tự hex.")

        results = simulate_games(md5_hash, num_games)
        tai_total = sum([results[key] for key in results if "Tài" in key])
        xiu_total = sum([results[key] for key in results if "Xỉu" in key])

        response = {
            "total_tai": tai_total,
            "total_xiu": xiu_total,
            "results": results,
            "final_result": "Tài" if tai_total > xiu_total else "Xỉu" if tai_total < xiu_total else "Hòa"
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Lấy cổng từ biến môi trường PORT, nếu không có thì sử dụng cổng 4000
    port = int(os.environ.get('PORT', 4000))
    app.run(port=port)  # Không cần host ở đây
