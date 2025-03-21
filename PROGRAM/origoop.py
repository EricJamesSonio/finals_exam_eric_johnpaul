import json
from datetime import datetime, date
import random

class POSSystem:
    """Main POS System that integrates all modules."""
    
    def __init__(self):
        self.sales_report = SalesReport()
        self.inventory = Inventory()
        self.order_processor = OrderProcessor()
        self.employee_manager = EmployeeManager()
        self.ingredient_manager = IngredientManager()
        self.sales_register = SalesRegister()
        self.employee_management = EmployeeManagement() 
        self.table_management = TableManagement()
    
    def run(self):
        """Simulate system startup."""
        print("POS System Initialized")

class SalesRegister:
    def __init__(self):
        self.receipts_file = "receipts.json"

    def process_order(self, cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
        """Process an order, generate a receipt, and save it to receipts.json."""

        # Step 1: Calculate totals
        subtotal = sum(item["price"] * item["quantity"] for item in cart)
        discount = subtotal * discount_rate
        tax = (subtotal - discount) * tax_rate
        total_payable = subtotal - discount + tax
        change = paid_amount - total_payable
        receipt_no = f"R{random.randint(10000, 99999)}"  # Random receipt number

        # Step 2: Create a receipt dictionary
        receipt = {
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

        # Step 3: Save to receipts.json
        try:
            with open(self.receipts_file, "r") as file:
                receipts = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            receipts = []  # If the file is missing or empty, start a new list

        receipts.append(receipt)

        with open(self.receipts_file, "w") as file:
            json.dump(receipts, file, indent=4)

        return receipt
    def calculate_totals(self, cart, discount_rate=0.0, tax_rate=0.0):
        """Calculate totals for an order including discount and tax."""
        subtotal = sum(item["price"] * item["quantity"] for item in cart)
        discount = subtotal * discount_rate
        tax = (subtotal - discount) * tax_rate
        total_payable = subtotal - discount + tax

        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total_payable": total_payable
        }
    
# ==========================
# FILE MANAGER CLASS
# ==========================

class FileManager:
    """Handles file operations for JSON storage."""
    
    @staticmethod
    def load_json(filename):
        """Load JSON data from a file."""
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_json(filename, data):
        """Save JSON data to a file."""
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

# ==========================
# SALES REPORT CLASS
# ==========================
class SalesReport:
    """Handles sales reporting."""
    
    SALES_REPORT_FILE = "sales_report.json"
    
    def __init__(self, top_sales_file="top_sales.json", receipts_file="receipts.json", return_report_file="return_report.json"):
        self.sales_data = FileManager.load_json(self.SALES_REPORT_FILE)
        self.top_sales_file = top_sales_file
        self.receipts_file = receipts_file
        self.return_report_file = return_report_file 

    def get_sales(self, date=None, month=None, today=False):
        """Fetch sales report based on date, month, or today's sales."""
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
        """Retrieve the top sales based on the given date."""
        try:
            with open(self.top_sales_file, "r") as file:
                top_sales_data = json.load(file)

            if date:
                return [sale for sale in top_sales_data if sale["date"] == date]
            return top_sales_data
        except FileNotFoundError:
            return "Top sales data file not found."
        except json.JSONDecodeError:
            return "Error reading top sales data."

    def calculate_total_sales(self, sales_data):
        """Calculate the total sales amount."""
        return sum(sale['total'] for sale in sales_data)

    def calculate_total_profit(self, sales_data):
        """Calculate total profit from sales."""
        return sum(sale.get('profit', 0) for sale in sales_data)

    def generate_summary(self, date=None, month=None, today=False):
        """Generate sales summary including total sales and profit."""
        report = self.get_sales(date, month, today)
        return {
            'total_sales': self.calculate_total_sales(report),
            'total_profit': self.calculate_total_profit(report),
            'sales_data': report
        }
    
    def find_receipt(self, receipt_no):
        """Find a receipt by its receipt number."""
        try:
            with open(self.receipts_file, "r") as file:
                receipts = json.load(file)

            for receipt in receipts:
                if receipt["receipt_no"] == receipt_no:
                    return receipt
            return f"Receipt {receipt_no} not found."
        except FileNotFoundError:
            return "Receipts data file not found."
        except json.JSONDecodeError:
            return "Error reading receipts data."
        
    def get_return_report(self, date=None):
        """Retrieve return report filtered by date."""
        try:
            with open(self.return_report_file, "r") as file:
                return_data = json.load(file)

            if date:
                filtered_returns = [r for r in return_data if r["date_returned"] == date]
                return filtered_returns

            return return_data  # Return all if no date specified
        except FileNotFoundError:
            return "Return report file not found."
        except json.JSONDecodeError:
            return "Error reading return report data."
        
    def get_return_report(self, date=None):
        """Retrieve return report data for a specific date."""
        try:
            with open(self.return_report_file, "r") as file:
                return_data = json.load(file)
                if date:
                    return [entry for entry in return_data if entry["date_returned"] == date]
                return return_data
        except FileNotFoundError:
            return []
    
    def calculate_total_returns(self, return_data):
        """Calculate total returned amount, discounts, and taxes."""
        total = sum(item['total'] for item in return_data)
        total_discount = sum(item.get('discount', 0) for item in return_data)
        total_tax = sum(item.get('tax', 0) for item in return_data)

        return {
            'total_returned': total,
            'total_discount': total_discount,
            'total_tax': total_tax
        }


# ==========================
# INVENTORY CLASS
# ==========================
class Inventory:
    """Handles inventory operations."""
    
    INVENTORY_FILE = "inventory.json"

    def __init__(self):
        self.items = FileManager.load_json(self.INVENTORY_FILE)
        self.categories_file = "categories.json"

    def add_item(self, item_data):
        """Add a new item to inventory.json."""
        try:
            with open(self.INVENTORY_FILE, "r") as file:
                inventory = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            inventory = []  # If the file doesn't exist, start with an empty list

        # Validate existing items before checking for duplicates
        for item in inventory:
            if "code" not in item:
                print(f"Warning: An item in inventory.json is missing 'code' and will be ignored.")
                continue  # Skip this item

            if item["code"] == item_data["code"]:
                return f"Item '{item_data['name']}' already exists in inventory."

        inventory.append(item_data)

        with open(self.INVENTORY_FILE, "w") as file:
            json.dump(inventory, file, indent=4)

        return f"Item '{item_data['name']}' added successfully!"

    
    def get_item_list(self):
        """Retrieve all items in inventory."""
        return self.items

    def get_item(self, item_code):
        """Retrieve an item by its code."""
        for item in self.items:
            if item["code"] == item_code:
                return item
        return None

    def update_inventory(self, cart):
        """Update inventory after a sale."""
        for cart_item in cart:
            for item in self.items:
                if item["code"] == cart_item["code"]:
                    item["quantity"] -= cart_item["quantity"]
                    break
        FileManager.save_json(self.INVENTORY_FILE, self.items)

    def add_category(self, category_name):
        """Add a new category to categories.json."""
        try:
            with open(self.categories_file, "r") as file:
                categories = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            categories = []  # If the file doesn't exist, start with an empty list

        if category_name in categories:
            return f"Category '{category_name}' already exists."

        categories.append(category_name)

        with open(self.categories_file, "w") as file:
            json.dump(categories, file, indent=4)

        return f"Category '{category_name}' added successfully!"
    
    def get_low_stock_items(self, threshold=5):
        """Retrieve items that are low in stock."""
        low_stock_items = [item for item in self.items if item.get("quantity", 0) <= threshold]

        if not low_stock_items:
            return "No low stock items."

        return low_stock_items
    
    def get_expired_items(self):
        """Retrieve items that have expired."""
        today = datetime.today().strftime('%Y-%m-%d')

        expired_items = [
            item for item in self.items
            if "expiration_date" in item and item["expiration_date"] < today
        ]

        if not expired_items:
            return "No expired items."

        return expired_items



# ==========================
# ORDER PROCESSOR CLASS
# ==========================
class OrderProcessor:
    """Processes orders and updates inventory."""
    
    SALES_REPORT_FILE = "sales_report.json"

    def __init__(self):
        self.sales_report = SalesReport()
        self.inventory = Inventory()

    def calculate_totals(self, cart, discount_rate=0.0, tax_rate=0.0):
        """Calculate order totals including discount and tax."""
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

    def process_order(self, cart, paid_amount, payment_type, discount_rate=0.0, tax_rate=0.0):
        """Process an order, update inventory, and save the sale."""
        totals = self.calculate_totals(cart, discount_rate, tax_rate)
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

        sales_data = FileManager.load_json(self.SALES_REPORT_FILE)
        sales_data.append(sale_entry)
        FileManager.save_json(self.SALES_REPORT_FILE, sales_data)

        self.inventory.update_inventory(cart)
        return sale_entry


# ==========================
# EMPLOYEE MANAGER CLASS
# ==========================
class EmployeeManager:
    """Manages employee records and work hours."""
    
    EMPLOYEES_FILE = "employees.json"
    WORK_SHEET_FILE = "work_sheet.json"

    def __init__(self):
        self.employees = FileManager.load_json(self.EMPLOYEES_FILE)

    def add_employee(self, name, address, contact_no, dob, user_type, login_id, password):
        """Add a new employee."""
        new_employee = {
            "id": len(self.employees) + 1,
            "name": name,
            "address": address,
            "contact_no": contact_no,
            "dob": dob,
            "user_type": user_type,
            "login_id": login_id,
            "password": password
        }
        self.employees.append(new_employee)
        FileManager.save_json(self.EMPLOYEES_FILE, self.employees)
        return new_employee

class EmployeeManagement:
    """Handles employee-related operations."""
    
    EMPLOYEE_FILE = "employees.json"
    WORKSHEET_FILE = "worksheet.json"

    def __init__(self):
        self.employees = FileManager.load_json(self.EMPLOYEE_FILE)
        self.worksheet = FileManager.load_json(self.WORKSHEET_FILE)

    def get_employee_list(self):
        """Retrieve all employees."""
        return self.employees
    
    def add_employee(self, name, address, contact_no, dob, user_type, login_id, password):
        """Add a new employee to the system."""
        new_employee = {
            "id": len(self.employees) + 1,  # Auto-increment ID
            "name": name,
            "address": address,
            "contact_no": contact_no,
            "date_of_birth": dob,
            "user_type": user_type,
            "login_id": login_id,
            "password": password
        }

        self.employees.append(new_employee)
        FileManager.save_json(self.EMPLOYEE_FILE, self.employees)  # Save to file

        return f"Employee {name} added successfully!"
    
    def update_employee(self, emp_id, name=None, address=None, contact_no=None, dob=None, user_type=None, login_id=None, password=None):
        """Update an existing employee's details."""
        for employee in self.employees:
            if employee["id"] == emp_id:
                if name: employee["name"] = name
                if address: employee["address"] = address
                if contact_no: employee["contact_no"] = contact_no
                if dob: employee["date_of_birth"] = dob
                if user_type: employee["user_type"] = user_type
                if login_id: employee["login_id"] = login_id
                if password: employee["password"] = password
                
                FileManager.save_json(self.EMPLOYEE_FILE, self.employees)  # Save changes
                return f"Employee ID {emp_id} updated successfully!"
        
        return f"Employee ID {emp_id} not found."
    
    def track_work_hours(self, username, date, time_in=None, time_out=None):
        """Track employee work hours with optional manual entry."""

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")  # Default to today

        if time_in:
            # Check if the employee already clocked in today
            for record in self.worksheet:
                if record["username"] == username and record["date"] == date:
                    return f"{username} has already clocked in on {date}."

        # Clock in
            new_entry = {
                "username": username,
                "date": date,
                "in": f"{date} {time_in}:00",  # Format time properly
                "out": None,
                "hours": None
            }
            self.worksheet.append(new_entry)
            FileManager.save_json(self.WORKSHEET_FILE, self.worksheet)
            return f"{username} clocked IN at {time_in} on {date}."

        elif time_out:
            # Find the existing record and update it
            for record in self.worksheet:
                if record["username"] == username and record["date"] == date and record["out"] is None:
                    record["out"] = f"{date} {time_out}:00"
                    in_time = datetime.strptime(record["in"], "%Y-%m-%d %H:%M:%S")
                    out_time = datetime.strptime(record["out"], "%Y-%m-%d %H:%M:%S")
                    record["hours"] = str(out_time - in_time)
                    FileManager.save_json(self.WORKSHEET_FILE, self.worksheet)
                    return f"{username} clocked OUT at {time_out} on {date}. Total hours: {record['hours']}."

            return f"{username} has not clocked IN on {date}."

        else:
            return "Please provide 'time_in' or 'time_out'."

        
# ==========================
# INGREDIENT MANAGER CLASS
# ==========================
class IngredientManager:
    """Handles ingredient deduction when food is ordered."""
    
    FOOD_MENU_FILE = "food_menu.json"
    INGREDIENTS_FILE = "ingredients_inventory.json"

    def __init__(self):
        self.food_menu = FileManager.load_json(self.FOOD_MENU_FILE)
        self.ingredients = FileManager.load_json(self.INGREDIENTS_FILE)

    def deduct_ingredients(self, order_item_name, quantity=1):
        """Deduct the required ingredients when a food item is ordered."""
        food_item = next((item for item in self.food_menu if item["name"] == order_item_name), None)

        if not food_item:
            return f"Error: '{order_item_name}' not found in menu."

        if "ingredients" not in food_item:
            return f"Error: '{order_item_name}' has no ingredients listed."

        for ingredient in food_item["ingredients"]:
            ingredient_name = ingredient["name"]
            required_qty = ingredient["quantity"] * quantity

            for stock in self.ingredients:
                if stock["name"].lower() == ingredient_name.lower():
                    if stock["quantity"] >= required_qty:
                        stock["quantity"] -= required_qty
                    else:
                        return f"Warning: Not enough stock for '{ingredient_name}'."

                    stock["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
            else:
                return f"Error: '{ingredient_name}' not found in inventory."

        FileManager.save_json(self.INGREDIENTS_FILE, self.ingredients)
        return f"Ingredients deducted for '{order_item_name}' (x{quantity})."
    
class TableManagement:
    """Handles restaurant table assignments and availability."""
    
    TABLES_FILE = "tables.json"

    def __init__(self):
        self.tables = FileManager.load_json(self.TABLES_FILE)

    def get_available_tables(self):
        """Return a list of available (vacant) tables."""
        return [table for table in self.tables if table["status"] == "Vacant"]

    def assign_table(self, order_no, seating_needed):
        """Assign a vacant table based on seating capacity and mark it as occupied."""
        for table in self.tables:
            if table["status"] == "Vacant" and table["seating_capacity"] >= seating_needed:
                table["status"] = "Occupied"
                table["current_order_no"] = order_no
                FileManager.save_json(self.TABLES_FILE, self.tables)
                return f"✅ Table {table['table_no']} assigned to order {order_no}."
        
        return "❌ No available table for the required seating capacity."

    def vacate_table(self, table_no):
        """Mark a table as vacant after customers leave."""
        for table in self.tables:
            if table["table_no"] == table_no and table["status"] == "Occupied":
                table["status"] = "Vacant"
                table["current_order_no"] = None
                FileManager.save_json(self.TABLES_FILE, self.tables)
                return f"✅ Table {table_no} is now available."

        return f"❌ Table {table_no} is already vacant or does not exist."

if __name__ == "__main__":
    pos = POSSystem()
    pos.run()