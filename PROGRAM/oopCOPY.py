import json
from datetime import datetime, date
from abc import ABC, abstractmethod
import random
from decimal import Decimal, ROUND_HALF_UP

# ==========================
# POS SYSTEM CLASS
# ==========================

class POSSystem:
    def __init__(self):
        self.sales_report = SalesReport()
        self.inventory = Inventory()
        self.order_processor = OrderProcessor()
        self.ingredient_manager = IngredientManager()
        self.sales_register = SalesRegister(self.order_processor)
        self.employee_management = EmployeeManagement() 
        self.table_management = TableManagement()
    
    def run(self):
        print("POS System Initialized")

# ==========================
# SALES REGISTER CLASS
# ==========================

class SalesRegister:
    RECEIPTS_FILE = "receipts.json"

    def __init__(self, order_processor):
        self.order_processor = order_processor 
        self.receipts = self.load_receipts()

    def load_receipts(self):
        self.receipts = FileManager.load_json(self.RECEIPTS_FILE) or []
        return self.receipts


    def save_receipts(self):
        with open(self.RECEIPTS_FILE, "w") as file:
            json.dump(self.receipts, file, indent=4)

    def load_cart(self):
        """Load the cart from cart.json"""
        try:
            with open("cart.json", "r") as file:
                cart_data = json.load(file)
                return cart_data.get("cart", []) 
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError("🚨 Error: cart.json is missing or corrupted!")

    def process_order(self, cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
        print("\nDEBUG: Received Cart for Order Processing:", cart)

        if isinstance(cart, dict) and "cart" in cart:
            cart = cart["cart"]  

        if not isinstance(cart, list):
            raise ValueError("🚨 Error: Cart data must be a list of items.")

        for item in cart:
            if "code" not in item:
                raise ValueError(f"🚨 Error: Missing 'code' in cart item: {item}")

        totals = self.order_processor.calculate_totals(cart, discount_rate, tax_rate)
        payment_strategy = self.order_processor.get_payment_strategy(payment_type)
        payment_result = payment_strategy.process_payment(totals["total_payable"], paid_amount)

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
            **payment_result
        }

        sales_data = FileManager.load_json(self.RECEIPTS_FILE)
        if not isinstance(sales_data, list):
            sales_data = []  

        sales_data.append(sale_entry)
        FileManager.save_json(self.RECEIPTS_FILE, sales_data)

        self.order_processor.inventory.update_inventory(cart)  
        return sale_entry
    
class Receipt:
    @staticmethod
    def create(cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
        
        subtotal = sum(item["price"] * item["quantity"] for item in cart)
        discount = subtotal * discount_rate
        tax = (subtotal - discount) * tax_rate
        total_payable = subtotal - discount + tax
        change = paid_amount - total_payable
        receipt_no = f"R{random.randint(10000, 99999)}" 

        return {
            "receipt_no": receipt_no,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": cart,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total_payable": total_payable,
            "paid_amount": paid_amount,
            "change": change,
            "payment_type": payment_type
        }
    
# ==========================
# FILE MANAGER CLASS
# ==========================

class FileManager: # SINGLETON
    @staticmethod
    def load_json(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"🚨 Warning: {file_path} not found. Returning empty list.")
            return []
        except json.JSONDecodeError:
            print(f"🚨 Error: {file_path} is corrupted. Resetting file.")
            FileManager.save_json(file_path, [])  
            return []

    @staticmethod
    def save_json(file_path, data):
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"🚨 Error: Failed to save {file_path}: {e}")


# ==========================
# SALES REPORT CLASS
# ==========================

class ReportStrategy(ABC):
    
    @abstractmethod
    def generate(self, sales_data):
        pass

class JSONReportStrategy(ReportStrategy):
    
    def generate(self, sales_data):
        return json.dumps(sales_data, indent=4)

class SalesReport:
    
    SALES_REPORT_FILE = "sales_report.json"
    
    def __init__(self, 
                 top_sales_file="top_sales.json", 
                 receipts_file="receipts.json", 
                 return_report_file="return_report.json", 
                 report_strategy=JSONReportStrategy()):
        self.sales_data = FileManager.load_json(self.SALES_REPORT_FILE)
        self.top_sales_file = top_sales_file
        self.receipts_file = receipts_file
        self.return_report_file = return_report_file
        self.report_strategy = report_strategy

    def get_sales(self, date=None, month=None, today=False):
        now = datetime.now()
        filtered_sales = []

        for sale in self.sales_data:
            sale_date = sale['date']
            sale_month = sale_date[:7]

            if today and sale_date == now.strftime('%Y-%m-%d'):
                filtered_sales.append(sale)
            elif month and sale_month == month:
                filtered_sales.append(sale)
            elif date and sale_date == date:
                filtered_sales.append(sale)

        return filtered_sales
    
    def get_top_sales(self, date=None):
        top_sales_data = FileManager.load_json(self.top_sales_file)
        return [sale for sale in top_sales_data if sale["date"] == date] if date else top_sales_data

    def calculate_total_sales(self, sales_data):
        return sum(sale['total'] for sale in sales_data)

    def calculate_total_profit(self, sales_data):
        return sum(sale.get('profit', 0) for sale in sales_data)

    def generate_summary(self, date=None, month=None, today=False):
        report = self.get_sales(date, month, today)
        summary = {
            'total_sales': self.calculate_total_sales(report),
            'total_profit': self.calculate_total_profit(report),
            'sales_data': report
        }
        return self.report_strategy.generate(summary) 

    def find_receipt(self, receipt_no):
        receipts = FileManager.load_json(self.receipts_file)
        return next((r for r in receipts if r["receipt_no"] == receipt_no), f"Receipt {receipt_no} not found.")

    def get_return_report(self, date=None):
        return_data = FileManager.load_json(self.return_report_file)
        return [r for r in return_data if r["date_returned"] == date] if date else return_data
    
    def calculate_total_returns(self, return_data):
        return {
            'total_returned': sum(item['total'] for item in return_data),
            'total_discount': sum(item.get('discount', 0) for item in return_data),
            'total_tax': sum(item.get('tax', 0) for item in return_data)
        }

# ==========================
# INVENTORY CLASS
# ==========================

class InventoryRepository:
    INVENTORY_FILE = "inventory.json"
    CATEGORIES_FILE = "categories.json"

    @staticmethod
    def load_inventory():
        try:
            with open(InventoryRepository.INVENTORY_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] 

    @staticmethod
    def save_inventory(inventory):
        with open(InventoryRepository.INVENTORY_FILE, "w") as file:
            json.dump(inventory, file, indent=4)

    @staticmethod
    def load_categories():
        try:
            with open(InventoryRepository.CATEGORIES_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_categories(categories):
        with open(InventoryRepository.CATEGORIES_FILE, "w") as file:
            json.dump(categories, file, indent=4)

class Inventory:
    
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Inventory, cls).__new__(cls)
            cls._instance.items = InventoryRepository.load_inventory()
            cls._instance.categories = InventoryRepository.load_categories()
        return cls._instance

    def add_item(self, item_data):
        if any(item["code"] == item_data["code"] for item in self.items):
            return f"Item '{item_data['name']}' already exists in inventory."

        self.items.append(item_data)
        InventoryRepository.save_inventory(self.items)
        return f"Item '{item_data['name']}' added successfully!"

    def get_item_list(self):
        self.items = InventoryRepository.load_inventory()  
        return self.items

    def get_item(self, item_code):
        return next((item for item in self.items if item["code"] == item_code), None)

    def update_inventory(self, cart_item):
        print("DEBUG CART ITEM:", cart_item)  

        if not isinstance(cart_item, dict):
            raise TypeError(f"Expected a dictionary, got {type(cart_item)} instead.")

        if "code" not in cart_item:
            raise KeyError("Missing 'code' in cart_item dictionary")

        try:
            with open("cart.json", "r") as file:
                cart_items = json.load(file) 
        except (FileNotFoundError, json.JSONDecodeError):
            cart_items = [] 

        print("DEBUG CART DATA BEFORE UPDATE:", cart_items)  

        for item in cart_items:
            if "code" not in item:
                raise KeyError(f"Cart item is missing 'code': {item}")

            if item["code"] == cart_item["code"]:
                item["quantity"] -= cart_item["quantity"]
                break 

        with open("cart.json", "w") as file:
            json.dump(cart_items, file, indent=4)

        print("UPDATED CART DATA:", cart_items)  
    
    def add_category(self, category_name):
        if category_name in self.categories:
            return f"Category '{category_name}' already exists."

        self.categories.append(category_name)
        InventoryRepository.save_categories(self.categories)
        return f"Category '{category_name}' added successfully!"

    def get_low_stock_items(self, threshold=5):
        return [item for item in self.items if item.get("quantity", 0) <= threshold]

    def get_expired_items(self):
        today = datetime.today().strftime('%Y-%m-%d')
        return [item for item in self.items if item.get("expiration_date", "9999-12-31") < today]

# ==========================
# ORDER PROCESSOR CLASS
# ==========================

class PaymentStrategy(ABC): # STRATEGY PATTERN

    @abstractmethod
    def process_payment(self, total, paid_amount):
        pass

class CashPayment(PaymentStrategy):
    def process_payment(self, total, paid_amount):
        total = Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        paid_amount = Decimal(paid_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        change = (paid_amount - total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        print(f"DEBUG: total={total}, paid_amount={paid_amount}, raw_change={change}")

        if paid_amount < total:
            remaining_due = (total - paid_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            print(f"DEBUG: remaining_due={remaining_due}") 
            return {
                "error": "Insufficient payment. Please pay the full amount.",
                "total_due": str(total), 
                "paid_amount": str(paid_amount),
                "remaining_due": str(remaining_due) 
            }

        return {
            "paid_amount": str(paid_amount),
            "change": str(change),
            "due": "0"
        }

    
class CreditCardPayment(PaymentStrategy):
    def process_payment(self, total, paid_amount):
        total = Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "paid_amount": str(total),
            "change": "0.00",
            "due": "0.00"
        }

class EWalletPayment(PaymentStrategy):
    def process_payment(self, total, paid_amount):
        total = Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "paid_amount": str(total),
            "change": "0.00",
            "due": "0.00"
        }
    

class OrderProcessor:

    SALES_REPORT_FILE = "sales_report.json"

    def __init__(self):
        self.sales_report = SalesReport()
        self.inventory = Inventory()

    def calculate_totals(self, cart, discount_rate=0.0, tax_rate=0.0):
        subtotal = Decimal(sum(item["price"] * item["quantity"] for item in cart)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        discount = Decimal(subtotal * Decimal(discount_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        tax = Decimal((subtotal - discount) * Decimal(tax_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_payable = Decimal(subtotal - discount + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_item_types = len(cart)

        print(f"DEBUG: subtotal={subtotal}, discount={discount}, tax={tax}, total_payable={total_payable}") 

        return {
            "subtotal": float(subtotal),
            "discount": float(discount),
            "tax": float(tax),
            "total_payable": float(total_payable),
            "total_item_types": total_item_types
        }

    def process_order(self, cart=None, paid_amount=0.0, payment_type="CASH", discount_rate=0.0, tax_rate=0.0):
        if cart is None:
            cart = FileManager.load_json("cart.json").get("cart", [])

        totals = self.calculate_totals(cart, discount_rate, tax_rate)
        payment_strategy = self.get_payment_strategy(payment_type)
        payment_result = payment_strategy.process_payment(totals["total_payable"], paid_amount)

        if "error" in payment_result:
            return payment_result 

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
            **payment_result
        }

        sales_data = FileManager.load_json(self.SALES_REPORT_FILE)
        sales_data.append(sale_entry)
        FileManager.save_json(self.SALES_REPORT_FILE, sales_data)

        for item in cart:
            self.inventory.update_inventory(item)
            IngredientManager().deduct_ingredients(item["name"], item["quantity"])

        return sale_entry
    
    def get_payment_strategy(self, payment_type):
        strategies = {
            "CASH": CashPayment(),
            "CREDIT CARD": CreditCardPayment(),
            "E-WALLET": EWalletPayment()
        }
        return strategies.get(payment_type.upper(), CashPayment())

# ==========================
# EMPLOYEE MANAGER CLASS
# ==========================

class EmployeeManagement: # SINGLETON & REPOSITORY PATTERN
    
    _instance = None  

    EMPLOYEE_FILE = "employees.json"
    WORKSHEET_FILE = "worksheet.json"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmployeeManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'employees'):
            self.employees = self._load_data(self.EMPLOYEE_FILE)
            self.worksheet = self._load_data(self.WORKSHEET_FILE)

    def _load_data(self, file_path):
        return FileManager.load_json(file_path)

    def _save_data(self, file_path, data):
        FileManager.save_json(file_path, data)

    def get_employee_list(self):
        return self.employees

    def add_employee(self, name, address, contact_no, dob, user_type, login_id, password):
        new_employee = {
            "id": len(self.employees) + 1,  
            "name": name,
            "address": address,
            "contact_no": contact_no,
            "date_of_birth": dob,
            "user_type": user_type,
            "login_id": login_id,
            "password": password
        }
        self.employees.append(new_employee)
        self._save_data(self.EMPLOYEE_FILE, self.employees)  

        return f"Employee {name} added successfully!"


        
# ==========================
# INGREDIENT MANAGER CLASS
# ==========================

class IngredientManager: # SINGLETON & REPOSITORY PATTERN
    
    _instance = None  

    FOOD_MENU_FILE = "food_menu.json"
    INGREDIENTS_FILE = "ingredients_inventory.json"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IngredientManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "food_menu"):  
            self.food_menu = self._load_data(self.FOOD_MENU_FILE)
            self.ingredients = self._load_data(self.INGREDIENTS_FILE)

    def add_food_item(self, category_id, name, description, price, ingredient_cost, ingredients, options=None):
        """ Add a new food item with a unique ID. """
        if any(item["name"].lower() == name.lower() for item in self.food_menu):
            return f"Error: Food item '{name}' already exists!"

        new_item_id = 1 if not self.food_menu else max(item["item_id"] for item in self.food_menu) + 1

        new_food_item = {
            "item_id": new_item_id,
            "category_id": category_id,
            "name": name,
            "description": description,
            "price": price,
            "ingredient_cost": ingredient_cost,
            "ingredients": ingredients,
            "options": options or {}
        }

        self.food_menu.append(new_food_item)
        self._save_data(self.FOOD_MENU_FILE, self.food_menu)

        return f"Food item '{name}' added successfully with Item ID: {new_item_id}!"
    
    def _load_data(self, file_path):
        return FileManager.load_json(file_path)

    def _save_data(self, file_path, data):
        FileManager.save_json(file_path, data)

    def _find_ingredient(self, name):
        return next((stock for stock in self.ingredients if stock["name"].lower() == name.lower()), None)

    def deduct_ingredients(self, item_id, quantity=1):
        """ Deducts required ingredients when an order is placed based on item_id. """
        food_item = next((item for item in self.food_menu if item["item_id"] == item_id), None)

        if not food_item:
            return f"Error: Food item with ID '{item_id}' not found in menu."

        if "ingredients" not in food_item:
            return f"Error: Food item with ID '{item_id}' has no ingredients listed."

        for ingredient_name, required_qty_per_item in food_item["ingredients"].items():
            required_qty = required_qty_per_item * quantity
            stock = self._find_ingredient(ingredient_name)

            if not stock:
                return f"Error: Ingredient '{ingredient_name}' not found in inventory."

            if stock["quantity"] < required_qty:
                return f"Warning: Not enough stock for '{ingredient_name}' (Needed: {required_qty}, Available: {stock['quantity']})."

            stock["quantity"] -= required_qty
            stock["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._save_data(self.INGREDIENTS_FILE, self.ingredients)
        return f"Ingredients deducted for food item ID '{item_id}' (x{quantity})."

# ==========================
# TABLE MANAGER CLASS
# ==========================

class Table:
    def __init__(self, table_no, seating_capacity, status="Vacant", current_order_no=None):
        self.table_no = table_no
        self.seating_capacity = seating_capacity
        self.status = status
        self.current_order_no = current_order_no

    def to_dict(self):
        return {
            "table_no": self.table_no,
            "seating_capacity": self.seating_capacity,
            "status": self.status,
            "current_order_no": self.current_order_no
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            table_no=data["table_no"],
            seating_capacity=data["seating_capacity"],
            status=data["status"],
            current_order_no=data["current_order_no"]
        )


class TableManagement:
    
    TABLES_FILE = "tables.json"

    def __init__(self):
        self.tables = [Table.from_dict(data) for data in FileManager.load_json(self.TABLES_FILE)]

    def _save_tables(self):
        FileManager.save_json(self.TABLES_FILE, [table.to_dict() for table in self.tables])

    def get_available_tables(self):
        return [table.to_dict() for table in self.tables if table.status == "Vacant"]

    def assign_table(self, order_no, seating_needed):
        for table in self.tables:
            if table.current_order_no == order_no:
                return f"❌ Order {order_no} is already assigned to Table {table.table_no}."

        for table in self.tables:
            if table.status == "Vacant" and table.seating_capacity >= seating_needed:
                table.status = "Occupied"
                table.current_order_no = order_no
                self._save_tables()
                return f"✅ Table {table.table_no} assigned to order {order_no}."

        return "❌ No available table for the required seating capacity."

    def vacate_table(self, table_no):
        for table in self.tables:
            if table.table_no == table_no and table.status == "Occupied":
                table.status = "Vacant"
                table.current_order_no = None
                self._save_tables()
                return f"✅ Table {table_no} is now available."

        return f"❌ Table {table_no} is already vacant or does not exist."


if __name__ == "__main__":
    pos = POSSystem()
    pos.run()
