
import sqlite3
import csv

conn = sqlite3.connect('Top100.db')
cursor = conn.cursor()


with open('Top100_list.csv','r',encoding='UTF-8-SIG') as trails:
    x = next(trails)
# print(x)
    count = 0  # 新增計數器

    r = csv.reader(trails)
    for x in r:
        # print(x)
        sql = f'''
        INSERT INTO HikingTrails (name, region, difficulty, time, url, img_url)
        VALUES (?, ?, ?, ?, ?, ?);
        '''
        # print(x)
        cursor.execute(sql,x) # 執行 SQL
        conn.commit()
        count += 1  # 每新增一筆就加一
    print(f'路線已新增 {count} 筆')
    trails.close()
    cursor.close()
    conn.close()