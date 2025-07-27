from flask import Flask, render_template, request
from datetime import datetime, date
from sqlalchemy import create_engine, text

app = Flask(__name__)

# ✅ DB 파일명 확인: 이름이 다르다면 여기서 수정하세요
engine = create_engine("sqlite:///celebrities_full.db", echo=False)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        birth_str = request.form["birthdate"]
        try:
            birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            today = date.today()
            weekday_name = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday = weekday_name[birth_date.weekday()]
            age_years = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age_years -= 1
            days_lived = (today - birth_date).days
            total_hours = days_lived * 24
            total_minutes = total_hours * 60
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_to_birthday = (next_birthday - today).days

            # ✅ MM-DD만 추출해서 DB에서 비교
            birth_mmdd = birth_str[-5:]

            with engine.connect() as conn:
                query = text("SELECT name FROM celebrities WHERE birth_mmdd = :mmdd")
                result_set = conn.execute(query, {"mmdd": birth_mmdd})
                celebrities = [row[0] for row in result_set]

            result = {
                "birth_str": birth_str,
                "weekday": weekday,
                "age_years": age_years,
                "days_lived": days_lived,
                "total_hours": total_hours,
                "total_minutes": total_minutes,
                "days_to_birthday": days_to_birthday,
                "celebrities": celebrities
            }

        except ValueError:
            result = {"error": "날짜 형식이 잘못되었습니다. 다시 입력해 주세요."}

    return render_template("index.html", result=result)
