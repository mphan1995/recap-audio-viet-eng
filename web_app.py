from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
load_dotenv()

from scripts.run_recap import run_recap
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recap", methods=["POST"])
def recap_api():
    if "file" not in request.files:
        return jsonify({"error":"No file uploaded"}), 400

    file = request.files["file"]
    os.makedirs("data/input", exist_ok=True)
    input_path = os.path.join("data/input", file.filename)
    file.save(input_path)

    result = run_recap(input_path)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
