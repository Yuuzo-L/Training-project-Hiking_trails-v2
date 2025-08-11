from flask import Flask, request, render_template
import sqlite3
import math

app = Flask(__name__)
DB_PATH = 'Trails.db'
PAGE_SIZE = 10

def get_difficulties_from_db():
    # 從資料庫取得所有實際存在的 difficulty 值
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT difficulty FROM HikingTrails WHERE difficulty IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    # 整理出現過的值
    existing = set(row[0] for row in rows if row[0].strip())

    # 用固定順序篩選出目前資料庫有的選項
    all_options = ["低", "低-中", "中", "中-高", "高"]
    filtered = [d for d in all_options if d in existing]

    return ["全部"] + filtered
# 這些可根據你的DB內容調整或擴充
REGIONS = ["全部", "北部", "中部", "南部", "東部", "外島", "香港","西班牙"]
DIFFICULTIES = get_difficulties_from_db()
TIMES = ["全部", "3小時內", "3-6小時", "6-12小時", "12小時-兩天"]  # 假設可篩
TYPES = ["全部", "百岳", "小百岳", "郊山", "百大必訪步道"]  # 假設有這欄
AREA_TO_CITIES = {
    "北部": ["台北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "宜蘭縣"],
    "中部": ["台中市", "彰化縣", "南投縣", "雲林縣", "苗栗縣"],
    "南部": ["台南市", "高雄市", "屏東縣", "嘉義市", "嘉義縣"],
    "東部": ["花蓮縣", "台東縣"],
    "外島": ["澎湖縣", "金門縣", "連江縣"],
}

CITY_TO_AREA = {}
for area, cities in AREA_TO_CITIES.items():
    for city in cities:
        CITY_TO_AREA[city] = area

TYPE_DB_MAP = {
    "百岳": "BaiYue.db",
    "小百岳": "XiaoBaiYue.db",
    "郊山": "foothills.db",
    "百大必訪步道": "Top100.db"
}
DEFAULT_DB = "Trails.db"  # 例如用來顯示全部或混合查詢時使用

def query_db(filters, page):
    offset = (page - 1) * PAGE_SIZE
    params = []
    where_clauses = []

    # ✅ 根據類型選擇資料庫
    db_path = TYPE_DB_MAP.get(filters['type'], DEFAULT_DB)

    # ✅ region 篩選條件（保留你原本的）
    if filters['region'] != "全部":
        cities = AREA_TO_CITIES.get(filters['region'])
        if cities:
            like_clauses = []
            for city in cities:
                like_clauses.append("region LIKE ?")
                like_clauses.append("region LIKE ?")
                params.append(f"%{city}%")
                params.append(f"%{city.replace('台', '臺')}%")
            where_clauses.append("(" + " OR ".join(like_clauses) + ")")
        else:
            where_clauses.append("(region LIKE ? OR region LIKE ?)")
            params.append(f"%{filters['region']}%")
            params.append(f"%{filters['region'].replace('台', '臺')}%")

    # ✅ 其他條件保持不變
    if filters['difficulty'] != "全部":
        where_clauses.append("difficulty = ?")
        params.append(filters['difficulty'])

    if filters['time'] != "全部":
        time_sql = """
        CASE
            WHEN time LIKE '%天%' THEN CAST(SUBSTR(time, 1, INSTR(time, '天') - 1) AS INTEGER) * 24
            WHEN time LIKE '%小時%' THEN
                CAST(SUBSTR(time, 1, INSTR(time, '小時') - 1) AS INTEGER) +
                CASE
                    WHEN time LIKE '%分鐘%' THEN
                        CAST(SUBSTR(time, INSTR(time, '小時') + 2, INSTR(time, '分鐘') - INSTR(time, '小時') - 2) AS INTEGER) / 60.0
                    ELSE 0
                END
            WHEN time LIKE '%分鐘%' THEN
                CAST(SUBSTR(time, 1, INSTR(time, '分鐘') - 1) AS INTEGER) / 60.0
            ELSE 0
        END
        """
        if filters['time'] == "3小時內":
            where_clauses.append(f"{time_sql} <= 3")
        elif filters['time'] == "3-6小時":
            where_clauses.append(f"{time_sql} > 3 AND {time_sql} <= 6")
        elif filters['time'] == "6-12小時":
            where_clauses.append(f"{time_sql} > 6 AND {time_sql} <= 12")
        elif filters['time'] == "12小時-兩天":
            where_clauses.append(f"{time_sql} > 12 AND {time_sql} <= 48")

    if filters['keyword']:
        where_clauses.append("name LIKE ?")
        params.append(f"%{filters['keyword']}%")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    count_sql = f"SELECT COUNT(*) FROM HikingTrails {where_sql}"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]

    sql = f"""
        SELECT name, region, difficulty, time, url , img_url
        FROM HikingTrails
        {where_sql}
        ORDER BY name
        LIMIT {PAGE_SIZE} OFFSET {offset}
    """
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    keys = ["name", "region", "difficulty", "time", "url", "img_url"]
    results = [dict(zip(keys, row)) for row in results]

    return results, total



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        region = request.form.get("region", "全部")
        difficulty = request.form.get("difficulty", "全部")
        time = request.form.get("time", "全部")
        type_ = request.form.get("type", "全部")
        keyword = request.form.get("keyword", "").strip()
        page = int(request.form.get("page", "1"))
    else:
        # GET初次進入或分頁切換
        region = request.args.get("region", "全部")
        difficulty = request.args.get("difficulty", "全部")
        time = request.args.get("time", "全部")
        type_ = request.args.get("type", "全部")
        keyword = request.args.get("keyword", "").strip()
        page = int(request.args.get("page", "1"))

    filters = {
        "region": region,
        "difficulty": difficulty,
        "time": time,
        "type": type_,
        "keyword": keyword,
    }

    results, total = query_db(filters, page)
    total_pages = math.ceil(total / PAGE_SIZE)

    return render_template(
        "index.html",
        regions=REGIONS,
        difficulties=DIFFICULTIES,
        times=TIMES,
        types=TYPES,
        selected_region=region,
        selected_difficulty=difficulty,
        selected_time=time,
        selected_type=type_,
        keyword=keyword,
        results=results,
        total=total,
        page=page,
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(debug=True)
