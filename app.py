from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
from sqlalchemy import create_engine, text
import json
import os
import pandas as pd # pandas 라이브러리 임포트

app = Flask(__name__)

# ✅ DB 파일명 확인
engine = create_engine("sqlite:///celebrities_full.db", echo=False)

# --- 새로운 코드 추가 시작 ---
# CSV 데이터 로드 (앱 시작 시 한 번만 로드)
BILLBOARD_CSV_PATH = "static/data/Billboard_Weekly_No1_with_Youtube.csv"
try:
    # Flask 앱의 루트 디렉토리를 기준으로 경로 설정
    base_dir = os.path.abspath(os.path.dirname(__file__))
    full_csv_path = os.path.join(base_dir, BILLBOARD_CSV_PATH)
    billboard_df = pd.read_csv(full_csv_path)
    billboard_df["chart_date"] = pd.to_datetime(billboard_df["chart_date"])
    print(f"Billboard CSV loaded successfully from: {full_csv_path}")
except FileNotFoundError:
    billboard_df = pd.DataFrame() # 파일이 없으면 빈 DataFrame 생성
    print(f"Error: Billboard CSV file not found at {full_csv_path}. Please ensure it exists.")
except Exception as e:
    billboard_df = pd.DataFrame()
    print(f"Error loading Billboard CSV: {e}")

def get_billboard_hit(birthdate):
    # birthdate: datetime.date 객체
    if billboard_df.empty:
        return None # DataFrame이 비어있으면 데이터 없음
        
    birth_ts = pd.Timestamp(birthdate)
    
    # birthdate보다 같거나 이전의 chart_date 중 가장 가까운 것
    # 내림차순 정렬 후 첫 번째 (가장 가까운 과거 날짜)
    filtered = billboard_df[billboard_df["chart_date"] <= birth_ts].sort_values(by="chart_date", ascending=False)
    
    if not filtered.empty:
        nearest = filtered.iloc[0] # 가장 가까운 과거 날짜의 데이터
        return {
            "chart_date": nearest["chart_date"].strftime("%Y-%m-%d"),
            "song": nearest["song"],
            "performer": nearest["performer"],
            "youtube": nearest["youtube_search_link"]
        }
    return None
# --- 새로운 코드 추가 끝 ---


@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        # 드롭다운으로부터 값 받아오기
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")

        # ✅ 유효성 검사
        if not (year and month and day):
            result = {"error": "생년, 월, 일을 모두 선택해 주세요."}
            return render_template("index.html", result=result)

        try:
            birth_str = f"{year}-{int(month):02d}-{int(day):02d}"
            birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()

            today = date.today()
            weekday_name = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday = weekday_name[birth_date.weekday()]

            age_years = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age_years -= 1

            korean_age = today.year - birth_date.year + 1

            days_lived = (today - birth_date).days
            total_hours = days_lived * 24
            total_minutes = total_hours * 60

            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_to_birthday = (next_birthday - today).days

            birth_mmdd = birth_date.strftime("%m-%d")

            with engine.connect() as conn:
                query = text("SELECT name FROM celebrities WHERE birth_mmdd = :mmdd")
                result_set = conn.execute(query, {"mmdd": birth_mmdd})
                celebrities = [row[0] for row in result_set]

            zodiac_sign = get_zodiac_sign(birth_date.month, birth_date.day)
            chinese_zodiac = get_chinese_zodiac(birth_date.year)
            generation = get_generation(birth_date.year)

            # --- 빌보드 1위 곡 정보 추가 ---
            billboard_hit = get_billboard_hit(birth_date)
            # --- 빌보드 1위 곡 정보 추가 끝 ---

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
                "celebrities": celebrities,
                "birth_year": birth_date.year,
                "birth_month": birth_date.month,
                "billboard_hit": billboard_hit # 빌보드 1위 곡 정보 추가
            }

        except ValueError:
            result = {"error": "유효하지 않은 날짜입니다. 다시 확인해 주세요."}
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
        ((12, 31), "염소자리"),
    ]
    for (m, d), name in zodiac:
        if (month, day) <= (m, d):
            return name
    return "염소자리"

# 🐉 띠 계산 함수
def get_chinese_zodiac(year):
    zodiacs = [
        "쥐", "소", "호랑이", "토끼", "용", "뱀",
        "말", "양", "원숭이", "닭", "개", "돼지"
    ]
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
