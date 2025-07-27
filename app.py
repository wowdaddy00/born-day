from flask import Flask, render_template, request
from datetime import datetime, date

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        birth_str = request.form["birthdate"]
        try:
            birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            today = date.today()

            # 1️⃣ 태어난 요일 계산
            weekday_name = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday = weekday_name[birth_date.weekday()]

            # 2️⃣ 현재 나이 계산 (만 나이)
            age_years = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age_years -= 1

            # 3️⃣ 생일부터 오늘까지 며칠 지났는지
            days_lived = (today - birth_date).days

            # 4️⃣ 총 시간, 분
            total_hours = days_lived * 24
            total_minutes = total_hours * 60

            # 5️⃣ 다음 생일까지 며칠 남았는지
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_to_birthday = (next_birthday - today).days

            # 결과 딕셔너리로 전달
            result = {
                "birth_str": birth_str,
                "weekday": weekday,
                "age_years": age_years,
                "days_lived": days_lived,
                "total_hours": total_hours,
                "total_minutes": total_minutes,
                "days_to_birthday": days_to_birthday,
            }

        except ValueError:
            result = {"error": "날짜 형식이 잘못되었습니다. 다시 입력해 주세요."}

    return render_template("index.html", result=result)
