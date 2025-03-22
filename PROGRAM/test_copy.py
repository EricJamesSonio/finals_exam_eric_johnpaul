import json
from decimal import Decimal
from datetime import datetime
from oopCOPY import FileManager,OrderProcessor, EmployeeManagement, IngredientManager, TableManagement  

# ==============
# TESTING SCRIPT
# ==============

def test_order_processing():
    print("\n==================== TEST: ORDER PROCESSING ====================")
    order_processor = OrderProcessor()
    try:
        with open("cart.json", "r") as file:
            test_cart = json.load(file)
        
        if not test_cart:
            print("Error: cart.json is empty.")
            return

    except FileNotFoundError:
        print("Error: cart.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: cart.json contains invalid JSON data.")
        return

    print("\n▶ Testing CASH Payment")
    cash_result = order_processor.process_order(cart=test_cart, paid_amount=500.00, payment_type="CASH")
    print(json.dumps(cash_result, indent=4))

    print("\n▶ Testing CREDIT CARD Payment")
    credit_result = order_processor.process_order(cart=test_cart, paid_amount=0.00, payment_type="CREDIT CARD")
    print(json.dumps(credit_result, indent=4))

    print("\n▶ Testing E-WALLET Payment")
    ewallet_result = order_processor.process_order(cart=test_cart, paid_amount=0.00, payment_type="E-WALLET")
    print(json.dumps(ewallet_result, indent=4))



def test_employee_management():
    print("\n==================== TEST: EMPLOYEE MANAGEMENT ====================")
    emp_manager = EmployeeManagement()

    print("\n▶ Adding a new employee...")
    '''emp_result = emp_manager.add_employee("Eric james", "123 Street", "09123456789", "2004-07-20", "Cashier", "Eric", "password123")
    print(emp_result) '''

    print("\n▶ Fetching employee list...")
    employee_list = emp_manager.get_employee_list()
    print(json.dumps(employee_list, indent=4))


def test_ingredient_management():
    print("\n==================== TEST: INGREDIENT MANAGEMENT ====================")
    ingredient_manager = IngredientManager()

    food_menu = FileManager.load_json("food_menu.json")

    if not food_menu:
        print("Error: food_menu.json is empty or not found.")
        return

    food_item_1 = food_menu[0] 
    food_item_2 = food_menu[1] if len(food_menu) > 1 else None  

    print(f"\n▶ Deducting ingredients for '{food_item_1['name']}' x2 (ID: {food_item_1['item_id']})")
    ingredient_result = ingredient_manager.deduct_ingredients(food_item_1["item_id"], quantity=2)
    print(ingredient_result)

    if food_item_2:
        print(f"\n▶ Deducting ingredients for '{food_item_2['name']}' x1 (ID: {food_item_2['item_id']})")
        ingredient_result = ingredient_manager.deduct_ingredients(food_item_2["item_id"], quantity=1)
        print(ingredient_result)

    print("\n▶ Deducting ingredients for a non-existent food item (ID: 999)")
    ingredient_result = ingredient_manager.deduct_ingredients(18, quantity=1)
    print(ingredient_result)

def test_table_management():
    print("\n==================== TEST: TABLE MANAGEMENT ====================")
    table_manager = TableManagement()

    print("\n▶ Fetching available tables...")
    available_tables = table_manager.get_available_tables()
    print(json.dumps(available_tables, indent=4))

    print("\n▶ Assigning table for order #12345 with seating 4")
    table_result = table_manager.assign_table("12345", 4)
    print(table_result)

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
