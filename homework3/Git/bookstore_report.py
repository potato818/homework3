import sqlite3

def print_sale_report(conn: sqlite3.Connection) -> None:
    """
    顯示所有銷售記錄。
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.sdate, m.mname, b.btitle, s.sqty, s.sdiscount, s.stotal
        FROM sale s
        JOIN member m ON s.mid = m.mid
        JOIN book b ON s.bid = b.bid
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
