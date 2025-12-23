"""
Pharmacy Functions - AI Voice Agent Tools

These functions are called by Deepgram when the AI needs to perform actions.
Think of these as the "skills" your AI agent has.
"""

import random
import string
from datetime import datetime, timedelta

# =============================================================================
# SIMULATED DATABASE
# =============================================================================

# Drug inventory
INVENTORY = {
    "aspirin": {"price": 5.99, "stock": 50, "requires_prescription": False},
    "ibuprofen": {"price": 7.99, "stock": 20, "requires_prescription": False},
    "acetaminophen": {"price": 6.49, "stock": 35, "requires_prescription": False},
    "tylenol": {"price": 8.99, "stock": 40, "requires_prescription": False},
    "advil": {"price": 9.49, "stock": 25, "requires_prescription": False},
    "benadryl": {"price": 11.99, "stock": 15, "requires_prescription": False},
    "zyrtec": {"price": 14.99, "stock": 30, "requires_prescription": False},
    "claritin": {"price": 12.99, "stock": 28, "requires_prescription": False},
    "pepto bismol": {"price": 8.49, "stock": 22, "requires_prescription": False},
    "tums": {"price": 4.99, "stock": 60, "requires_prescription": False},
    "amoxicillin": {"price": 15.99, "stock": 10, "requires_prescription": True},
    "lisinopril": {"price": 12.49, "stock": 8, "requires_prescription": True},
    "metformin": {"price": 9.99, "stock": 12, "requires_prescription": True},
}

# Orders storage (in-memory for demo)
ORDERS = {}


# =============================================================================
# FUNCTION IMPLEMENTATIONS
# =============================================================================

def get_drug_info(drug_name: str) -> str:
    """
    Get the price and stock availability of a specific drug.
    
    Args:
        drug_name: The name of the drug to look up
        
    Returns:
        A string describing the drug's price and availability
    """
    drug_key = drug_name.lower().strip()
    
    # Check exact match first
    drug = INVENTORY.get(drug_key)
    
    # If no exact match, try partial match
    if not drug:
        for name, info in INVENTORY.items():
            if drug_key in name or name in drug_key:
                drug = info
                drug_key = name
                break
    
    if drug:
        availability = "in stock" if drug["stock"] > 0 else "out of stock"
        prescription_note = " (requires prescription)" if drug["requires_prescription"] else ""
        
        if drug["stock"] > 0:
            return (
                f"{drug_key.title()} is ${drug['price']:.2f} and we have "
                f"{drug['stock']} units {availability}{prescription_note}."
            )
        else:
            return f"Sorry, {drug_key.title()} is currently out of stock."
    
    return f"Sorry, we don't carry {drug_name}. Would you like me to suggest an alternative?"


def place_order(drug_name: str, quantity: int, customer_name: str) -> str:
    """
    Place an order for a specific drug.
    
    Args:
        drug_name: The name of the drug to order
        quantity: The quantity to order
        customer_name: The customer's name
        
    Returns:
        A confirmation string with order details
    """
    drug_key = drug_name.lower().strip()
    drug = INVENTORY.get(drug_key)
    
    # Try partial match
    if not drug:
        for name, info in INVENTORY.items():
            if drug_key in name or name in drug_key:
                drug = info
                drug_key = name
                break
    
    if not drug:
        return f"Sorry, we don't carry {drug_name}. Cannot place order."
    
    if drug["requires_prescription"]:
        return (
            f"{drug_key.title()} requires a prescription. "
            "Please bring your prescription to the pharmacy to complete this order."
        )
    
    if drug["stock"] < quantity:
        return (
            f"Sorry, we only have {drug['stock']} units of {drug_key.title()} in stock. "
            f"Would you like to order {drug['stock']} instead?"
        )
    
    # Generate order ID
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Calculate totals
    subtotal = drug["price"] * quantity
    tax = subtotal * 0.08  # 8% tax
    total = subtotal + tax
    
    # Estimate pickup time
    pickup_time = datetime.now() + timedelta(minutes=30)
    
    # Store order
    ORDERS[order_id] = {
        "customer_name": customer_name,
        "drug_name": drug_key,
        "quantity": quantity,
        "total": total,
        "status": "processing",
        "pickup_time": pickup_time.strftime("%I:%M %p"),
        "created_at": datetime.now()
    }
    
    # Update inventory
    INVENTORY[drug_key]["stock"] -= quantity
    
    return (
        f"Order confirmed! Order ID: {order_id}. "
        f"{quantity} units of {drug_key.title()} for {customer_name}. "
        f"Total: ${total:.2f} including tax. "
        f"Ready for pickup at {pickup_time.strftime('%I:%M %p')}."
    )


def check_order_status(order_id: str) -> str:
    """
    Check the status of an existing order.
    
    Args:
        order_id: The order ID to look up
        
    Returns:
        A string describing the order status
    """
    order = ORDERS.get(order_id.upper().strip())
    
    if not order:
        return (
            f"I couldn't find an order with ID {order_id}. "
            "Please double-check the order number and try again."
        )
    
    return (
        f"Order {order_id.upper()} for {order['customer_name']}: "
        f"{order['quantity']} units of {order['drug_name'].title()}. "
        f"Status: {order['status']}. "
        f"Ready for pickup at {order['pickup_time']}. "
        f"Total: ${order['total']:.2f}."
    )


# =============================================================================
# FUNCTION DISPATCHER
# =============================================================================

def execute_function(function_name: str, parameters: dict) -> str:
    """
    Dispatch function calls from Deepgram to the appropriate handler.
    
    Args:
        function_name: The name of the function to execute
        parameters: The parameters to pass to the function
        
    Returns:
        The result string from the function
    """
    functions = {
        "get_drug_info": get_drug_info,
        "place_order": place_order,
        "check_order_status": check_order_status,
    }
    
    func = functions.get(function_name)
    if func:
        try:
            return func(**parameters)
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    return f"Unknown function: {function_name}"


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    # Test the functions
    print("=== Testing Pharmacy Functions ===\n")
    
    print("1. Getting drug info:")
    print(f"   {get_drug_info('aspirin')}")
    print(f"   {get_drug_info('unknown_drug')}")
    print()
    
    print("2. Placing an order:")
    print(f"   {place_order('ibuprofen', 2, 'John Smith')}")
    print()
    
    print("3. Checking order status:")
    # Get the order ID from the ORDERS dict
    if ORDERS:
        order_id = list(ORDERS.keys())[0]
        print(f"   {check_order_status(order_id)}")
    print()
    
    print("=== Tests Complete ===")
