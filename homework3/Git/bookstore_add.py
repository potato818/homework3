import sqlite3
from typing import Tuple
from datetime import datetime

DB_NAME = "bookstore.db"

# 連線資料庫
def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化資料表及初始資料
def initialize_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS member (
        mid TEXT PRIMARY KEY,
        mname TEXT NOT NULL,
        mphone TEXT NOT NULL,
        memail TEXT
    );

    CREATE TABLE IF NOT EXISTS book (
        bid TEXT PRIMARY KEY,
        btitle TEXT NOT NULL,
        bprice INTEGER NOT NULL,
        bstock INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sale (
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        sdate TEXT NOT NULL,
        mid TEXT NOT NULL,
        bid TEXT NOT NULL,
        sqty INTEGER NOT NULL,
        sdiscount INTEGER NOT NULL,
        stotal INTEGER NOT NULL
    );

    INSERT OR IGNORE INTO member VALUES ('M001', 'Alice', '0912-345678', 'alice@example.com');
    INSERT OR IGNORE INTO member VALUES ('M002', 'Bob', '0923-456789', 'bob@example.com');
    INSERT OR IGNORE INTO member VALUES ('M003', 'Cathy', '0934-567890', 'cathy@example.com');

    INSERT OR IGNORE INTO book VALUES ('B001', 'Python Programming', 600, 50);
    INSERT OR IGNORE INTO book VALUES ('B002', 'Data Science Basics', 800, 30);
    INSERT OR IGNORE INTO book VALUES ('B003', 'Machine Learning Guide', 1200, 20);

    INSERT OR IGNORE INTO sale (sid, sdate, mid, bid, sqty, sdiscount, stotal) VALUES (1, '2024-01-15', 'M001', 'B001', 2, 100, 1100);
    INSERT OR IGNORE INTO sale (sid, sdate, mid, bid, sqty, sdiscount, stotal) VALUES (2, '2024-01-16', 'M002', 'B002', 1, 50, 750);
    INSERT OR IGNORE INTO sale (sid, sdate, mid, bid, sqty, sdiscount, stotal) VALUES (3, '2024-01-17', 'M001', 'B003', 3, 200, 3400);
    INSERT OR IGNORE INTO sale (sid, sdate, mid, bid, sqty, sdiscount, stotal) VALUES (4, '2024-01-18', 'M003', 'B001', 1, 0, 600);
    """)
    conn.commit()

# 新增銷售記錄
def add_sale(conn: sqlite3.Connection, sdate: str, mid: str, bid: str, sqty: int, sdiscount: int) -> tuple[bool, str]:
    try:
        cursor = conn.cursor()

        # 檢查會員是否存在
        cursor.execute("SELECT * FROM member WHERE mid = ?", (mid,))
        if not cursor.fetchone():
            return False, "錯誤：會員編號無效"

        # 檢查書籍是否存在
        cursor.execute("SELECT * FROM book WHERE bid = ?", (bid,))
        book = cursor.fetchone()
        if not book:
            return False, "錯誤：書籍編號無效"

        bprice = book["bprice"]
        bstock = book["bstock"]

        # 檢查庫存
        if sqty > bstock:
            return False, f"錯誤：書籍庫存不足 (現有庫存: {bstock})"

        # 計算總額
        stotal = bprice * sqty - sdiscount

        # 寫入銷售記錄並更新庫存
        cursor.execute("BEGIN")  # 開始交易
        cursor.execute("""
            INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sdate, mid, bid, sqty, sdiscount, stotal))

        # 更新庫存
        cursor.execute("UPDATE book SET bstock = bstock - ? WHERE bid = ?", (sqty, bid))

        # 提交更改
        conn.commit()  # 確保資料提交

        return True, f"銷售記錄已新增！(銷售總額: {stotal:,})"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"資料庫錯誤：{str(e)}"

# 顯示銷售報表
def print_sale_report(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.sdate, m.mname, b.btitle, s.sqty, s.sdiscount, s.stotal
        FROM sale s
        JOIN member m ON s.mid = m.mid
        JOIN book b ON s.bid = b.bid
        ORDER BY s.sdate
    """)
    sales = cursor.fetchall()

    if sales:
        print("\n********* 銷售報表 *********")
        print(f"{'日期':<15} {'會員名稱':<10} {'書名':<30} {'數量':<5} {'折扣':<5} {'總額':<10}")
        print("-" * 75)
        for sale in sales:
            print(f"{sale['sdate']:<15} {sale['mname']:<10} {sale['btitle']:<30} {sale['sqty']:<5} {sale['sdiscount']:<5} {sale['stotal']:<10}")
        print("-" * 75)
    else:
        print("無銷售記錄。")

# 主程式進入點
def main() -> None:
    with connect_db() as conn:
        initialize_db(conn)

        while True:
            print("""
***************選單***************
1. 新增銷售記錄
2. 顯示銷售報表
3. 更新銷售記錄
4. 刪除銷售記錄
5. 離開
**********************************
            """)
            choice = input("請選擇操作項目(Enter 離開)：").strip()
            if choice == "":
                continue
            elif choice == "1":
                sdate = input("請輸入銷售日期 (YYYY-MM-DD)：")
                mid = input("請輸入會員編號：")
                bid = input("請輸入書籍編號：")
                sqty = int(input("請輸入銷售數量："))
                sdiscount = int(input("請輸入折扣金額："))
                success, message = add_sale(conn, sdate, mid, bid, sqty, sdiscount)
                print(message)
            elif choice == "2":
                print_sale_report(conn)
            elif choice == "3":
                print("更新銷售記錄功能尚未實作")
            elif choice == "4":
                print("刪除銷售記錄功能尚未實作")
            elif choice == "5":
                break
            else:
                print("=> 請輸入有效的選項（1-5）")

if __name__ == "__main__":
    main()
