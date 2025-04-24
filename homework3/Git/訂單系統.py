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
def add_sale(conn: sqlite3.Connection, sdate: str, mid: str, bid: str, sqty: int, sdiscount: int) -> Tuple[bool, str]:
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
        cursor.execute("UPDATE book SET bstock = bstock - ? WHERE bid = ?", (sqty, bid))
        conn.commit()
        return True, f"銷售記錄已新增！(銷售總額: {stotal:,})"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"資料庫錯誤：{str(e)}"

# 顯示銷售報表
def print_sale_report(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sale.sid, sale.sdate, member.mname, book.btitle, sale.sqty, sale.sdiscount, sale.stotal
        FROM sale
        JOIN member ON sale.mid = member.mid
        JOIN book ON sale.bid = book.bid
    """)
    sales = cursor.fetchall()
    print("銷售報表：")
    print(f"{'ID':<5} {'日期':<15} {'會員姓名':<10} {'書名':<25} {'數量':<6} {'折扣':<6} {'總額':<10}")
    for sale in sales:
        print(f"{sale['sid']:<5} {sale['sdate']:<15} {sale['mname']:<10} {sale['btitle']:<25} {sale['sqty']:<6} {sale['sdiscount']:<6} {sale['stotal']:<10}")

# 更新銷售記錄
def update_sale(conn: sqlite3.Connection) -> None:
    """
    更新銷售記錄，允許修改銷售數量和折扣。
    """
    try:
        cursor = conn.cursor()

        # 請用戶輸入銷售記錄的ID
        sid = int(input("請輸入要更新的銷售記錄ID："))

        # 檢查銷售記錄是否存在
        cursor.execute("SELECT * FROM sale WHERE sid = ?", (sid,))
        sale_record = cursor.fetchone()
        if not sale_record:
            print("錯誤：銷售記錄ID不存在")
            return

        print(f"當前銷售記錄：{sale_record}")

        # 提供更新選項
        sqty = int(input("請輸入新的購買數量："))
        sdiscount = int(input("請輸入新的折扣金額："))

        # 查詢書籍的價格
        cursor.execute("SELECT bprice FROM book WHERE bid = ?", (sale_record["bid"],))
        book = cursor.fetchone()
        if not book:
            print("錯誤：書籍編號無效")
            return

        bprice = book["bprice"]
        stotal = bprice * sqty - sdiscount

        # 更新銷售記錄
        cursor.execute("""
            UPDATE sale
            SET sqty = ?, sdiscount = ?, stotal = ?
            WHERE sid = ?
        """, (sqty, sdiscount, stotal, sid))

        # 更新庫存
        cursor.execute("UPDATE book SET bstock = bstock + ? WHERE bid = ?", (sale_record["sqty"], sale_record["bid"]))  # 先加回原來的庫存
        cursor.execute("UPDATE book SET bstock = bstock - ? WHERE bid = ?", (sqty, sale_record["bid"]))  # 再減去新的數量

        conn.commit()
        print("銷售記錄更新成功！")
    
    except sqlite3.Error as e:
        print(f"資料庫錯誤：{str(e)}")
        conn.rollback()

# 刪除銷售記錄
def delete_sale(conn: sqlite3.Connection) -> None:
    """
    刪除銷售記錄
    """
    try:
        cursor = conn.cursor()

        # 請用戶輸入銷售記錄的ID
        sid = int(input("請輸入要刪除的銷售記錄ID："))

        # 檢查銷售記錄是否存在
        cursor.execute("SELECT * FROM sale WHERE sid = ?", (sid,))
        sale_record = cursor.fetchone()
        if not sale_record:
            print("錯誤：銷售記錄ID不存在")
            return

        # 更新庫存
        cursor.execute("UPDATE book SET bstock = bstock + ? WHERE bid = ?", (sale_record["sqty"], sale_record["bid"]))  # 恢復庫存

        # 刪除銷售記錄
        cursor.execute("DELETE FROM sale WHERE sid = ?", (sid,))

        conn.commit()
        print("銷售記錄刪除成功！")
    
    except sqlite3.Error as e:
        print(f"資料庫錯誤：{str(e)}")
        conn.rollback()

# 主程式進入點
def main() -> None:
    with connect_db() as conn:
        initialize_db(conn)

        while True:
            print("""***************選單***************
1. 新增銷售記錄
2. 顯示銷售報表
3. 更新銷售記錄
4. 刪除銷售記錄
5. 離開
**********************************""")
            choice = input("請選擇操作項目(Enter 離開)：")
            if choice == "1":
                sdate = input("請輸入銷售日期 (YYYY-MM-DD)：")
                mid = input("請輸入會員ID：")
                bid = input("請輸入書籍ID：")
                sqty = int(input("請輸入購買數量："))
                sdiscount = int(input("請輸入折扣金額："))
                success, msg = add_sale(conn, sdate, mid, bid, sqty, sdiscount)
                print(msg)
            elif choice == "2":
                print_sale_report(conn)
            elif choice == "3":
                update_sale(conn)
            elif choice == "4":
                delete_sale(conn)
            elif choice == "5":
                break
            else:
                print("無效選擇，請重新輸入。")

if __name__ == "__main__":
    main()
