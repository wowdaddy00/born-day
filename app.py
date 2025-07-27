from flask import Flask, render_template, request
from datetime import datetime, date
from sqlalchemy import create_engine, text

app = Flask(__name__)

# ✅ DB 파일명 확인: 이름이 다르다면 여기서 수정하세요
engine = create_engine("sqlite:///celebrities_full.db", echo=False)

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        # HTML 폼에서 'birthdate' 필드로 YYYY-MM-DD 형식의 문자열을 받습니다.
        birth_str_input = request.form.get("birthdate")

        try:
            # 받은 문자열을 datetime.date 객체로 변환
            birth_date = datetime.strptime(birth_str_input, "%Y-%m-%d").date()
            birth_str = birth_str_input # 원본 문자열을 결과에 사용

            today = date.today()
            weekday_name = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday = weekday_name[birth_date.weekday()]

            age_years = today.year - birth_date.year
            # 만 나이 계산 (생일이 지났는지 여부 확인)
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age_years -= 1

            # 한국 나이 계산 (만 나이 + 1)
            korean_age = today.year - birth_date.year + 1

            days_lived = (today - birth_date).days
            total_hours = days_lived * 24
            total_minutes = total_hours * 60

            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_to_birthday = (next_birthday - today).days

            # ✅ MM-DD만 추출해서 DB에서 비교
            birth_mmdd = birth_date.strftime("%m-%d") # datetime 객체에서 MM-DD 형식으로 변환

            with engine.connect() as conn:
                query = text("SELECT name FROM celebrities WHERE birth_mmdd = :mmdd")
                result_set = conn.execute(query, {"mmdd": birth_mmdd})
                celebrities = [row[0] for row in result_set]

            zodiac_sign = get_zodiac_sign(birth_date.month, birth_date.day)
            chinese_zodiac = get_chinese_zodiac(birth_date.year)
            generation = get_generation(birth_date.year)

            result = {
                "birth_str": birth_str,
                "weekday": weekday,
                "age_years": age_years,
                "korean_age": korean_age,
                "zodiac_sign": zodiac_sign,
                "chinese_zodiac": chinese_zodiac,
                "generation": generation,
                "days_lived": days_lived,
                "total_hours": total_hours,
                "total_minutes": total_minutes,
                "days_to_birthday": days_to_birthday,
                "celebrities": celebrities
            }

        except ValueError:
            result = {"error": "날짜 형식이 잘못되었습니다. 다시 입력해 주세요."}
        except Exception as e:
            result = {"error": f"오류가 발생했습니다: {e}"}

    return render_template("index.html", result=result)

# 🌟 별자리 계산 함수
def get_zodiac_sign(month, day):
    zodiac = [
        ((1, 20), "염소자리"),
        ((2, 19), "물병자리"),
        ((3, 21), "물고기자리"),
        ((4, 20), "양자리"),
        ((5, 21), "황소자리"),
        ((6, 22), "쌍둥이자리"),
        ((7, 23), "게자리"),
        ((8, 23), "사자자리"),
        ((9, 24), "처녀자리"),
        ((10, 24), "천칭자리"),
        ((11, 23), "전갈자리"),
        ((12, 22), "사수자리"),
        ((12, 31), "염소자리"), # 12월 22일 이후는 다음 해 1월 19일까지 염소자리
    ]
    for (m, d), name in zodiac:
        if (month, day) <= (m, d):
            return name
    return "염소자리"  # 기본값 (이 부분은 사실상 12/22~12/31에 해당)

# 🐉 띠 계산 함수
def get_chinese_zodiac(year):
    zodiacs = [
        "쥐", "소", "호랑이", "토끼", "용", "뱀",
        "말", "양", "원숭이", "닭", "개", "돼지"
    ]
    # 1900년을 기준으로 쥐띠가 시작한다고 가정 (1900 % 12 = 4, 쥐띠)
    # 실제 띠는 입춘 기준이므로 단순 연도 계산은 오차가 있을 수 있음
    return zodiacs[(year - 1900) % 12]

# 👶 세대 구분 함수
def get_generation(year):
    if year < 1946:
        return "세계대전 이전 세대"
    elif year < 1965:
        return "베이비붐 세대"
    elif year < 1981:
        return "X세대"
    elif year < 1997:
        return "밀레니얼 세대"
    elif year < 2013:
        return "Z세대"
    else:
        return "알파 세대"

if __name__ == "__main__":
    app.run(debug=True)
