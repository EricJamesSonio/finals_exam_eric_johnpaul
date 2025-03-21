import json
from decimal import Decimal
from datetime import datetime
from oopCOPY import FileManager,OrderProcessor, EmployeeManagement, IngredientManager, TableManagement  # Import your main classes

# ==============
# TESTING SCRIPT
# ==============

def test_order_processing():
    print("\n==================== TEST: ORDER PROCESSING ====================")
    order_processor = OrderProcessor()

    # Fake cart
    test_cart = [
        {"code": "R1", "name": "Grilled Chicken", "price": 150.00, "quantity": 2},
        {"code": "G1", "name": "Grilled Pork", "price": 180.00, "quantity": 1}
    ]

    # Case 1: Paying with CASH
    print("\n▶ Testing CASH Payment")
    cash_result = order_processor.process_order(cart=test_cart, paid_amount=500.00, payment_type="CASH")
    print(json.dumps(cash_result, indent=4))

    # Case 2: Paying with CREDIT CARD
    print("\n▶ Testing CREDIT CARD Payment")
    credit_result = order_processor.process_order(cart=test_cart, paid_amount=0.00, payment_type="CREDIT CARD")
    print(json.dumps(credit_result, indent=4))

    # Case 3: Paying with E-WALLET
    print("\n▶ Testing E-WALLET Payment")
    ewallet_result = order_processor.process_order(cart=test_cart, paid_amount=0.00, payment_type="E-WALLET")
    print(json.dumps(ewallet_result, indent=4))


def test_employee_management():
    print("\n==================== TEST: EMPLOYEE MANAGEMENT ====================")
    emp_manager = EmployeeManagement()

    # Adding an employee
    print("\n▶ Adding a new employee...")
    emp_result = emp_manager.add_employee("John Doe", "123 Street", "09123456789", "1995-07-20", "Cashier", "johndoe", "password123")
    print(emp_result)

    # Fetching employee list
    print("\n▶ Fetching employee list...")
    employee_list = emp_manager.get_employee_list()
    print(json.dumps(employee_list, indent=4))


def test_ingredient_management():
    print("\n==================== TEST: INGREDIENT MANAGEMENT ====================")
    ingredient_manager = IngredientManager()

    # Load food menu from JSON
    food_menu = FileManager.load_json("food_menu.json")

    # Select some real food items from the JSON for testing
    if not food_menu:
        print("Error: food_menu.json is empty or not found.")
        return

    # Picking first two available items
    food_item_1 = food_menu[0]  # First item
    food_item_2 = food_menu[1] if len(food_menu) > 1 else None  # Second item (if available)

    print(f"\n▶ Deducting ingredients for '{food_item_1['name']}' x2 (ID: {food_item_1['item_id']})")
    ingredient_result = ingredient_manager.deduct_ingredients(food_item_1["item_id"], quantity=2)
    print(ingredient_result)

    if food_item_2:
        print(f"\n▶ Deducting ingredients for '{food_item_2['name']}' x1 (ID: {food_item_2['item_id']})")
        ingredient_result = ingredient_manager.deduct_ingredients(food_item_2["item_id"], quantity=1)
        print(ingredient_result)

    # Testing with a non-existent item ID
    print("\n▶ Deducting ingredients for a non-existent food item (ID: 999)")
    ingredient_result = ingredient_manager.deduct_ingredients(18, quantity=1)
    print(ingredient_result)

def test_table_management():
    print("\n==================== TEST: TABLE MANAGEMENT ====================")
    table_manager = TableManagement()

    # Get available tables
    print("\n▶ Fetching available tables...")
    available_tables = table_manager.get_available_tables()
    print(json.dumps(available_tables, indent=4))

    # Assigning a table
    print("\n▶ Assigning table for order #12345 with seating 4")
    table_result = table_manager.assign_table("12345", 4)
    print(table_result)

    # Vacating a table
    print("\n▶ Vacating Table #1")
    vacate_result = table_manager.vacate_table(1)
    print(vacate_result)


# ===================
# RUN ALL TEST CASES
# ===================
if __name__ == "__main__":
    test_order_processing()
    test_employee_management()
    test_ingredient_management()
    test_table_management()
