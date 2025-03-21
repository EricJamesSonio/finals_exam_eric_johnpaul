import json
from datetime import datetime

SALES_REPORT_FILE = "sales_report.json"
TOP_SALES_FILE = "top_sales.json"
RECEIPTS_FILE = "receipts.json"
RETURN_REPORT_FILE = "return_report.json"
INVENTORY_FILE = "inventory.json"
CATEGORIES_FILE = "categories.json"
EMPLOYEES_FILE = "employees.json"
WORK_SHEET_FILE = "work_sheet.json"
FOOD_MENU_FILE = "food_menu.json"
KITCHEN_ORDERS_FILE = "kitchen_orders.json"
RESTAURANT_INFO_FILE = "restaurant_info.json"
INGREDIENTS_FILE = "ingredients_inventory.json"
TABLES_FILE = "tables.json"

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def load_employees():
    try:
        with open(EMPLOYEES_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_employees(data):
    with open(EMPLOYEES_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ========================
# SALES REPORT
# ========================

def get_sales_report(date=None, month=None, today=False):
    sales_data = load_json(SALES_REPORT_FILE)
    filtered_sales = []
    now = datetime.now()
    
    for sale in sales_data:
        sale_date = sale['date']  
        sale_month = sale_date[:7]  
        
        if today and sale_date == now.strftime('%Y-%m-%d'):
            filtered_sales.append(sale)
        elif month and sale_month == month:
            filtered_sales.append(sale)
        elif date and sale_date == date:
            filtered_sales.append(sale)
    
    return filtered_sales

def calculate_total_sales(sales_data):
    return sum(sale['total'] for sale in sales_data)

def calculate_total_profit(sales_data):
    return sum(sale.get('profit', 0) for sale in sales_data)

def generate_sales_summary(date=None, month=None, today=False):
    report = get_sales_report(date, month, today)
    total_sales = calculate_total_sales(report)
    total_profit = calculate_total_profit(report)
    
    return {
        'total_sales': total_sales,
        'total_profit': total_profit,
        'sales_data': report
    }

def get_top_sales(date=None):
    top_sales = load_json(TOP_SALES_FILE)
    if date:
        return [sale for sale in top_sales if sale['date'] == date]
    return top_sales

def find_receipt(receipt_no, date=None):
    receipts = load_json(RECEIPTS_FILE)
    for receipt in receipts:
        if receipt['receipt_no'] == receipt_no and (not date or receipt['date'] == date):
            return receipt
    return None

def get_return_report(date=None, from_date=None, to_date=None):
    return_data = load_json(RETURN_REPORT_FILE)
    filtered_returns = []
    
    for return_item in return_data:
        return_date = return_item['date_returned']
        if date and return_date == date:
            filtered_returns.append(return_item)
        elif from_date and to_date and from_date <= return_date <= to_date:
            filtered_returns.append(return_item)
    
    return filtered_returns

def calculate_total_returns(return_data):
    total = sum(item['total'] for item in return_data)
    total_discount = sum(item.get('discount', 0) for item in return_data)
    total_tax = sum(item.get('tax', 0) for item in return_data)
    
    return {
        'total_returned': total,
        'total_discount': total_discount,
        'total_tax': total_tax
    }

def load_sales_report():
    try:
        with open(SALES_REPORT_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_sales_report(data):
    with open(SALES_REPORT_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ========================
# INVENTORY
# ========================

def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as file:
            inventory = json.load(file)
            print("📦 Loaded Inventory:", inventory) 
            return inventory
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_inventory(data):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_item_list():
    return load_inventory()

def calculate_totals(cart, discount_rate=0.0, tax_rate=0.0):
    subtotal = sum(item["price"] * item["quantity"] for item in cart)
    discount = subtotal * discount_rate
    tax = (subtotal - discount) * tax_rate
    total_payable = subtotal - discount + tax
    total_item_types = len(cart)
    
    return {
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total_payable": total_payable,
        "total_item_types": total_item_types
    }

def process_payment(cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
    totals = calculate_totals(cart, discount_rate, tax_rate)
    change = paid_amount - totals["total_payable"]
    receipt_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
    date = datetime.now().strftime('%Y-%m-%d')
    
    sale_entry = {
        "date": date,
        "receipt_no": receipt_no,
        "items": cart,
        "total": totals["total_payable"],
        "discount": totals["discount"],
        "tax": totals["tax"],
        "payment_type": payment_type,
        "due": max(0, -change),
        "change": max(0, change)
    }
    
    sales_data = load_sales_report()
    sales_data.append(sale_entry)
    save_sales_report(sales_data)
    
    return sale_entry

def get_item_from_inventory(item_code):
    inventory = load_inventory()
    for item in inventory:
        if item["code"] == item_code:
            return item
    return None

def update_inventory(cart):
    inventory = load_inventory()
    
    for cart_item in cart:
        print("🔍 Processing Cart Item:", cart_item)  
        
        if "code" not in cart_item:
            print("🚨 Error: 'code' key missing in cart item:", cart_item)
            continue  

        for item in inventory:
            if "code" not in item:
                print("🚨 Error: 'code' key missing in inventory item:", item)
                continue  

            if item["code"] == cart_item["code"]:
                item["quantity"] -= cart_item["quantity"]
                break

    save_inventory(inventory)

def process_order(cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
    receipt = process_payment(cart, paid_amount, payment_type, discount_rate, tax_rate)
    update_inventory(cart)
    return receipt

def add_item(item):
    inventory = load_json(INVENTORY_FILE)
    inventory.append(item)
    save_json(INVENTORY_FILE, inventory)
    return f"Item {item['name']} added successfully!"

def add_category(category_name):
    categories = load_json(CATEGORIES_FILE)
    new_id = len(categories) + 1  
    categories.append({"id": new_id, "name": category_name})
    save_json(CATEGORIES_FILE, categories)
    return f"Category '{category_name}' added successfully!"

def get_low_stock_items(threshold=5):
    inventory = load_json(INVENTORY_FILE)
    return [item for item in inventory if item["quantity"] <= threshold]

def get_expired_items():
    inventory = load_json(INVENTORY_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    return [item for item in inventory if item["expiration_date"] < today]

# ========================
# DEDUCTION OF INGREDIENTS
# ========================

def deduct_ingredients(order_item_name, quantity=1):
    
    food_menu = load_json(FOOD_MENU_FILE)
    ingredients_inventory = load_json(INGREDIENTS_FILE)
    
    food_item = next((item for item in food_menu if item["name"] == order_item_name), None)
    
    if not food_item:
        return f"Error: '{order_item_name}' not found in menu."
    
    if "ingredients" not in food_item:
        return f"Error: '{order_item_name}' has no ingredients listed."

    for ingredient in food_item["ingredients"]:
        if isinstance(ingredient, str):  
            ingredient = json.loads(ingredient) 

        ingredient_name = ingredient.get("name", "")
        required_qty = ingredient["quantity"] * quantity
        
        for stock in ingredients_inventory:
            if stock["name"].lower() == ingredient_name.lower():
                if stock["quantity"] >= required_qty:
                    stock["quantity"] -= required_qty
                else:
                    return f"Warning: Not enough stock for '{ingredient_name}'."
        
                stock["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        else:
            return f"Error: '{ingredient_name}' not found in inventory."

    save_json(INGREDIENTS_FILE, ingredients_inventory)
    
    return f"Ingredients deducted for '{order_item_name}' (x{quantity})."

# ========================
# EMPLOYEE
# ========================

def get_employee_list():
    return load_employees()

def add_employee(name, address, contact_no, dob, user_type, login_id, password):
    employees = load_employees()
    new_employee = {
        "id": len(employees) + 1,
        "name": name,
        "address": address,
        "contact_no": contact_no,
        "dob": dob,
        "user_type": user_type,
        "login_id": login_id,
        "password": password
    }
    employees.append(new_employee)
    save_employees(employees)
    return new_employee

def update_employee(emp_id, name=None, address=None, contact_no=None, dob=None, user_type=None, login_id=None, password=None):
    employees = load_employees()
    for emp in employees:
        if emp["id"] == emp_id:
            if name: emp["name"] = name
            if address: emp["address"] = address
            if contact_no: emp["contact_no"] = contact_no
            if dob: emp["dob"] = dob
            if user_type: emp["user_type"] = user_type
            if login_id: emp["login_id"] = login_id
            if password: emp["password"] = password
            save_employees(employees)
            return emp
    return None

def track_work_hours(username, date, time_in, time_out):
    try:
        fmt = "%H:%M"
        time_in_dt = datetime.strptime(time_in, fmt)
        time_out_dt = datetime.strptime(time_out, fmt)
        hours_worked = time_out_dt - time_in_dt
    except ValueError:
        return "Invalid time format. Use HH:MM"

    work_sheet = load_json(WORK_SHEET_FILE)
    work_sheet.append({
        "username": username,
        "date": date,
        "time_in": time_in,
        "time_out": time_out,
        "hours": str(hours_worked)
    })
    save_json(WORK_SHEET_FILE, work_sheet)
    return work_sheet[-1]

# ========================
# FOOD MENU
# ========================

def load_food_menu():
    try:
        with open(FOOD_MENU_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_food_menu(data):
    with open(FOOD_MENU_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_all_food_items():
    return load_food_menu()

def load_categories():
    try:
        with open(CATEGORIES_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_food_by_category(category_name):
    food_menu = load_food_menu()
    categories = load_categories()

    category_id = next((cat["id"] for cat in categories if cat["name"] == category_name), None)

    if category_id is None:
        return [] 

    return [item for item in food_menu if item.get("category_id") == category_id]

# ========================
# KITCHEN ORDERS
# ========================

def load_kitchen_orders():
    try:
        with open(KITCHEN_ORDERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_kitchen_orders(data):
    with open(KITCHEN_ORDERS_FILE, "w") as file:
        json.dump(data, file, indent=4)

def add_kitchen_order(order_no, table_no, order_type, food_items, quantity, special_notes, cashier_name):
    orders = load_kitchen_orders()
    new_order = {
        "order_no": order_no,
        "table_no": table_no,
        "order_type": order_type,  
        "food_items": food_items,
        "quantity": quantity,
        "special_notes": special_notes,
        "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "order_status": "Pending",
        "cashier_name": cashier_name
    }
    orders.append(new_order)
    save_kitchen_orders(orders)
    return new_order

def update_kitchen_order_status(order_no, new_status):
    orders = load_kitchen_orders()
    for order in orders:
        if order["order_no"] == order_no:
            order["order_status"] = new_status
            save_kitchen_orders(orders)
            return order
    return None

def get_all_kitchen_orders():
    return load_kitchen_orders()

def get_kitchen_orders_by_status(status):
    return [order for order in load_kitchen_orders() if order["order_status"] == status]

def load_restaurant_info():
    try:
        with open(RESTAURANT_INFO_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# ========================
# WORKSHEET
# ========================

def authenticate_user(login_id, password):
    employees = load_employees()
    for emp in employees:
        if emp["login_id"] == login_id and emp["password"] == password:
            return emp  
    return None 

def load_work_logs():
    try:
        with open(WORK_SHEET_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_work_logs(logs):
    with open(WORK_SHEET_FILE, "w") as file:
        json.dump(logs, file, indent=4)

def record_time_in(login_id):
    logs = load_work_logs()
    today = datetime.now().strftime("%Y-%m-%d")

    for log in logs:
        if log["username"] == login_id and log["date"] == today and log["time_out"] is None:
            return "Already clocked in today."

    logs.append({
        "username": login_id,
        "date": today,
        "time_in": datetime.now().strftime("%H:%M"),
        "time_out": None,
        "hours": None
    })
    
    save_work_logs(logs)
    return "Time-in recorded successfully."

def record_time_out(login_id):
    logs = load_work_logs()
    today = datetime.now().strftime("%Y-%m-%d")

    for log in logs:
        if log["username"] == login_id and log["date"] == today and log["time_out"] is None:
            log["time_out"] = datetime.now().strftime("%H:%M")

            time_in = datetime.strptime(log["time_in"], "%H:%M")
            time_out = datetime.strptime(log["time_out"], "%H:%M")
            total_hours = time_out - time_in

            log["hours"] = str(total_hours)
            save_work_logs(logs)
            return "Time-out recorded successfully."

    return "No active shift found for today."

def login(login_id, password):
    user = authenticate_user(login_id, password)
    if user:
        return record_time_in(login_id)  
    return "Invalid username or password."

def logout(login_id):
    return record_time_out(login_id)

# ========================
# TABLES
# ========================

def load_tables():
    try:
        with open(TABLES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_tables(tables):
    with open(TABLES_FILE, "w") as file:
        json.dump(tables, file, indent=4)

def get_available_tables():
    tables = load_tables()
    return [table for table in tables if table["status"] == "Vacant"]

def assign_table(order_no, seating_needed):
    tables = load_tables()

    for table in tables:
        if table["status"] == "Vacant" and table["seating_capacity"] >= seating_needed:
            table["current_order_no"] = order_no
            table["status"] = "Occupied"
            save_tables(tables)
            return f"Table {table['table_no']} assigned to Order {order_no}."

    return "No available table for the required seating capacity."

def mark_table_vacant(table_no):
    tables = load_tables()

    for table in tables:
        if table["table_no"] == table_no and table["status"] == "Occupied":
            table["current_order_no"] = None
            table["status"] = "Vacant"
            save_tables(tables)
            return f"Table {table_no} is now vacant."

    return f"Table {table_no} is already vacant or does not exist."

# ========================
# RESTAURANT DETAILS
# ========================

def get_restaurant_details():
    return load_restaurant_info()