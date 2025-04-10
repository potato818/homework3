import json
from typing import List, Dict, Tuple, Optional


INPUT_FILE = "orders.json"
OUTPUT_FILE = "output_orders.json"


def load_data(filename: str) -> List[Dict]:

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(filename: str, data: List[Dict]) -> None:

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def calculate_order_total(order: Dict) -> int:
  
    return sum(item["price"] * item["quantity"] for item in order["items"])


def print_order_report(orders: List[Dict], single: bool = False) -> None:
 
    if single:
        print("\n==================== 出餐訂單 ====================")
    else:
        print("\n==================== 訂單報表 ====================")

    for idx, order in enumerate(orders, 1):
        if not single:
            print(f"訂單 #{idx}")
        print(f"訂單編號: {order['order_id']}")
        print(f"顧客姓名: {order['customer']}")
        print("-" * 50)
        print("商品名稱\t單價\t數量\t小計")
        print("-" * 50)

        total = 0
        for item in order["items"]:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            print(f"{item['name']}\t{item['price']}\t{item['quantity']}\t{subtotal}")

        print("-" * 50)
        print(f"訂單總額: {total:,}")
        print("=" * 50)


def add_order(orders: List[Dict]) -> str:

    order_id = input("請輸入訂單編號：").upper()
    if any(order["order_id"] == order_id for order in orders):
        return f"=> 錯誤：訂單編號 {order_id} 已存在！"

    customer = input("請輸入顧客姓名：")
    items = []

    while True:
        name = input("請輸入商品名稱（Enter 結束）：")
        if name == "":
            break

        try:
            price = int(input("請輸入價格："))
            if price < 0:
                print("=> 錯誤：價格不能為負數")
                continue
            quantity = int(input("請輸入數量："))
            if quantity <= 0:
                print("=> 錯誤：數量必須為正整數")
                continue
        except ValueError:
            print("=> 錯誤：價格與數量必須為整數")
            continue

        items.append({"name": name, "price": price, "quantity": quantity})

    if not items:
        return "=> 錯誤：訂單必須包含至少一項商品"

    orders.append({"order_id": order_id, "customer": customer, "items": items})
    save_data(INPUT_FILE, orders)
    return f"=> 訂單 {order_id} 已新增！"


def process_order(orders: List[Dict]) -> Tuple[str, Optional[Dict]]:

    if not orders:
        return "=> 無待處理訂單！", None

    print("\n======== 待處理訂單列表 ========")
    for idx, order in enumerate(orders, 1):
        print(f"{idx}. 訂單編號: {order['order_id']} - 顧客: {order['customer']}")
    print("=" * 32)

    choice = input("請輸入要出餐的訂單編號（輸入數字，Enter 取消）：")
    if choice == "":
        return "=> 已取消出餐", None

    if not choice.isdigit() or not (1 <= int(choice) <= len(orders)):
        return "=> 錯誤：輸入無效，請輸入正確的數字", None

    idx = int(choice) - 1
    order = orders.pop(idx)

    done_orders = load_data(OUTPUT_FILE)
    done_orders.append(order)

    save_data(OUTPUT_FILE, done_orders)
    save_data(INPUT_FILE, orders)

    return f"=> 訂單 {order['order_id']} 已完成出餐", order


def print_menu() -> None:
 
    print("\n*************** 主選單 ***************")
    print("1. 新增訂單")
    print("2. 顯示訂單報表")
    print("3. 出餐處理")
    print("4. 離開")
    print("*************************************")


def main() -> None:

    while True:
        print_menu()
        choice = input("請選擇操作項目 (Enter 離開)：")

        if choice == "" or choice == "4":
            print("再見～")
            break

        orders = load_data(INPUT_FILE)

        if choice == "1":
            message = add_order(orders)
            print(message)
        elif choice == "2":
            if orders:
                print_order_report(orders)
            else:
                print("=> 無待處理訂單")
        elif choice == "3":
            message, order = process_order(orders)
            print(message)
            if order:
                print_order_report([order], single=True)
        else:
            print("=> 錯誤：請輸入 1-4 之間的選項")


if __name__ == "__main__":
    main()
