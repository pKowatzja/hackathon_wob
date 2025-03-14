from flask import Flask, request, jsonify, render_template
import json
import os
from werkzeug.utils import secure_filename

# from model import query_llm
from model import (
    process_damage_report,
)  # Assuming you'll create this file from your code

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "")
    response = ""  # query_llm(question)
    return jsonify(response)


@app.route("/process_report", methods=["POST"])
def process_report():
    try:
        # Get form data
        date = request.form.get("date", "")
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        category = request.form.get("category", "")

        # Process uploaded images
        image_paths = []
        if "images" in request.files:
            images = request.files.getlist("images")
            for image in images:
                if image.filename:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    image.save(image_path)
                    image_paths.append(image_path)

        # Create the damage report dictionary
        damage_report = {
            "date": date,
            "title": title,
            "description": description,
            "category": category,
            "image_paths": image_paths,
        }

        # Process the report using the LLM
        response = process_damage_report(damage_report)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
