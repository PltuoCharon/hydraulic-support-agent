import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    user="hs_user",
    password="zyb123",
    database="hydraulic_support",
    charset="utf8mb4"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS support_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(50),
    working_resistance_kn INT,
    note TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute(
    "INSERT INTO support_models (model_name, working_resistance_kn, note) VALUES (%s, %s, %s)",
    ("ZY12000/28/63D", 12000, "掩护式液压支架，联调测试数据")
)
conn.commit()

cursor.execute("SELECT * FROM support_models")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
print("全链路测试成功")
