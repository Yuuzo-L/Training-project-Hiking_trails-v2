import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://hiking.biji.co"
url = 'https://hiking.biji.co/index.php?q=trail&type=%E5%B0%8F%E7%99%BE%E5%B2%B3&filter=1&page='
headers = {"User-Agent": "Mozilla/5.0"}
trail_data = []
def fetch_data(page):
    response = requests.get(url + str(page), headers = headers)
    soup = BeautifulSoup(response.text, "html.parser")
    mountains = soup.find_all("div",class_="flex")
    temp_data = []
    for mt in mountains:
        name2 = mt.find("a",class_="w-56")
        name = mt.find("h2",class_="text-xl truncate")
        location = mt.find("div",class_="text-base text-gray-600 flex-1 truncate") # 地區
        time_f = mt.find("ul",class_="flex items-center space-x-2.5")
        difficulties = mt.find("div",class_="flex-1 relative p-5 space-y-2.5")
        if name2 and name and location and time_f and difficulties:
            train_name2 = name2.get("title") # 路線名
            a_tag = name.find("a") # 資訊連結
            time_li = time_f.find_all("li") # 所需時間
            img_tag = name2.find("img") # 圖片連結
            diff_tag = difficulties.find_all("li")
            if a_tag and len(time_li)>=3:
                location = location.text.strip()
                trail_time = time_li[2].text.strip().replace('所需時間 ','')
                link_href = a_tag['href'].strip()
                full_link = base_url + link_href
                img_url = img_tag['src']
                diff_tag2 = diff_tag[0].text.strip().replace("難度 ","")
                temp_data.append([train_name2, location, diff_tag2, trail_time,full_link,img_url])
    return temp_data

seen_names = set()  # 記錄已經出現過的步道名稱

for page in range(1,10):
    temp_data = fetch_data(page) # 抓一頁資料（是個 list）
    current_page_data = [] # 過濾完"暫存"的每頁資料
    for row in temp_data:
        if row[0] not in seen_names:  # 如果這個步道名稱沒看過
            seen_names.add(row[0])    # 加進去記錄下來
            trail_data.append(row)    # 然後才加入總資料清單
            current_page_data.append(row)
    print(f"載入...第{page}頁{current_page_data}")
    time.sleep(0.5)
print(f"共新增{len(seen_names)}個步道資料")

# 儲存 csv
df = pd.DataFrame(trail_data, columns=["步道名稱", "地區", "難度", "所需時間", "連結", "圖片連結"])
df.to_csv("XiaoBaiYue_list.csv",index =False, encoding="utf-8")
print('已存到 XiaoBaiYue_list.csv')