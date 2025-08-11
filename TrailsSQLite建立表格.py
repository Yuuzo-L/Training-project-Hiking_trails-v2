import sqlite3

conn =sqlite3.connect('Top100.db')
cursor = conn.cursor()

sql = '''
CREATE TABLE HikingTrails (
   name TEXT NOT NULL,
   region TEXT,
   difficulty TEXT,
   time TEXT,
   url TEXT,
   img_url TEXT
);
'''
print(sql)
cursor.execute(sql) # 創建表格
conn.commit() # 提交 保存

cursor.close()
conn.close()
print('Trails.db 建立')