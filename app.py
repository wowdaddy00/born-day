from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        birth_date = request.form["birthdate"]
        result = f"{birth_date}에 태어난 당신! 아직 준비 중인 기능입니다 😊"
    return render_template("index.html", result=result)

