from flask import Flask, request, jsonify, render_template
import json
from model import (
    query_llm,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "")
    response = query_llm(question)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
