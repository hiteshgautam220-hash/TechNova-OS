"""Synthetic Data Generator for TechNova Business Operations Assistant.
Generates customers.csv, products.csv, orders.csv, returns.csv, and seeds SQLite.
"""

import csv
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Paths
CURRENT_DIR = Path(__file__).resolve().parent
DATA_DIR = CURRENT_DIR
DB_PATH = DATA_DIR / "technova_business.db"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Products definition
PRODUCTS = [
    # Laptops
    ("PRD-101", "NovaBook Pro 16 (M3 Max/32GB)", "Laptops", 1799.00, 45),
    ("PRD-102", "NovaBook Air 14 (M2/16GB)", "Laptops", 1099.00, 80),
    ("PRD-103", "NovaBook Gaming 15 (RTX 4070)", "Laptops", 1399.00, 35),
    ("PRD-104", "NovaBook Ultra 13 (Portable)", "Laptops", 849.00, 60),
    
    # Smartphones
    ("PRD-201", "NovaPhone 15 Pro (256GB Titanium)", "Smartphones", 1199.00, 95),
    ("PRD-202", "NovaPhone 15 (128GB Midnight)", "Smartphones", 799.00, 110),
    ("PRD-203", "NovaPhone 14 Lite (64GB)", "Smartphones", 449.00, 75),
    ("PRD-204", "NovaPhone Max 15 (512GB Gold)", "Smartphones", 1349.00, 40),
    
    # Audio / Headphones
    ("PRD-301", "NovaSound ANC 700 (Noise-Canceling)", "Headphones", 299.00, 120),  # Intentionally high returns (defective batch)
    ("PRD-302", "NovaSound Sport Pods (Waterproof)", "Headphones", 149.00, 140),
    ("PRD-303", "NovaSound Studio Pro (Wired HiFi)", "Headphones", 389.00, 50),
    ("PRD-304", "NovaSound Wireless Lite (BT 5.3)", "Headphones", 69.00, 200),
    
    # Smartwatches
    ("PRD-401", "NovaWatch Ultra Pro (Titanium Cellular)", "Smartwatches", 499.00, 65),
    ("PRD-402", "NovaWatch Active 4 (Fitness/OLED)", "Smartwatches", 249.00, 90),
    ("PRD-403", "NovaWatch Fit Classic (Leather Band)", "Smartwatches", 179.00, 105),
    
    # Tablets
    ("PRD-501", "NovaPad Pro 12.9 (120Hz Liquid OLED)", "Tablets", 899.00, 55),
    ("PRD-502", "NovaPad Air 10.9 (Lightweight)", "Tablets", 549.00, 85),
    ("PRD-503", "NovaPad Mini 8.4 (Handheld)", "Tablets", 379.00, 90),
    
    # Accessories
    ("PRD-601", "NovaCharge 100W GaN 4-Port Fast Charger", "Accessories", 69.00, 300),
    ("PRD-602", "NovaHub 8-in-1 Dual 4K USB-C Dock", "Accessories", 59.00, 250),
    ("PRD-603", "NovaKey Mechanical RGB Keyboard", "Accessories", 129.00, 130),
    ("PRD-604", "NovaMouse Wireless Ergonomic Pro", "Accessories", 79.00, 180),
    ("PRD-605", "NovaPen Pro Stylus with Haptics", "Accessories", 99.00, 160),
    ("PRD-606", "NovaStand Aluminum Laptop Riser", "Accessories", 45.00, 220),
    ("PRD-607", "NovaCase Magnetic Smart Folio", "Accessories", 39.00, 350),
]

CITIES = ["Seattle, WA", "Austin, TX", "San Jose, CA", "Boston, MA", "Denver, CO", 
          "Chicago, IL", "New York, NY", "Atlanta, GA", "San Diego, CA", "Dallas, TX"]

FIRST_NAMES = ["Liam", "Olivia", "Noah", "Emma", "Oliver", "Charlotte", "James", "Amelia",
               "Elijah", "Sophia", "William", "Isabella", "Henry", "Ava", "Lucas", "Mia",
               "Benjamin", "Evelyn", "Theodore", "Harper", "Alexander", "Luna", "Daniel", "Camila",
               "Matthew", "Gianna", "Samuel", "Elizabeth", "David", "Eleanor", "Joseph", "Ella"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
              "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez"]

RETURN_REASONS = [
    ("Defective Audio Hardware / Bluetooth Disconnects", 0.40),
    ("Arrived Damaged in Transit", 0.20),
    ("Wrong Color / Model Sent", 0.15),
    ("Customer Changed Mind / Remorse", 0.15),
    ("Late Delivery Exceeded Window", 0.10)
]

def get_weighted_return_reason(product_id: str) -> str:
    # PRD-301 NovaSound ANC 700 specifically has defective audio issues
    if product_id == "PRD-301":
        if random.random() < 0.70:
            return "Defective Audio Hardware / Bluetooth Disconnects"
    choices, weights = zip(*RETURN_REASONS)
    return random.choices(choices, weights=weights, k=1)[0]


def generate_all_data():
    print("Generating synthetic dataset for TechNova Business Operations...")
    today = datetime(2026, 9, 20)
    
    # 1. Generate 160 Customers
    customers = []
    for i in range(1, 161):
        cid = f"CUST-{1000 + i}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        city = random.choice(CITIES)
        email = f"{first.lower()}.{last.lower()}{random.randint(10,99)}@example.com"
        phone = f"+1 (555) {random.randint(200,999):03d}-{random.randint(1000,9999):04d}"
        
        # Initial tiers, will be updated after computing orders
        customers.append({
            "customer_id": cid,
            "name": name,
            "email": email,
            "phone": phone,
            "city": city,
            "customer_type": "Standard",
            "total_orders": 0,
            "total_spent": 0.0,
            "last_order_date": "",
            "is_inactive": 0
        })

    # 2. Generate Orders over 120 days
    # To create a realistic "Why did sales fall this week?" scenario:
    # Week 1 (Current: Days 0 to 6 before today): Slump in sales (~$28k - $32k) due to supply constraints & high returns of PRD-301
    # Week 2 (Prior: Days 7 to 13 before today): Strong peak promotional sales (~$52k - $58k)
    # Week 3-16: Normal steady sales
    orders = []
    returns = []
    order_counter = 5001
    return_counter = 8001
    
    # Customer order frequency profiles
    # Some customers order frequently, some are inactive (haven't ordered in 60-100 days)
    inactive_customer_ids = set([c["customer_id"] for c in customers[100:140]]) # 40 inactive customers
    churn_risk_customer_ids = set([c["customer_id"] for c in customers[140:160]]) # 20 churn risk
    
    customer_stats = {c["customer_id"]: {"spent": 0.0, "orders": 0, "last_date": None} for c in customers}
    
    # Days from 120 down to 0
    for day_offset in range(120, -1, -1):
        order_date = today - timedelta(days=day_offset)
        date_str = order_date.strftime("%Y-%m-%d")
        
        # Determine order volume for the day
        if 0 <= day_offset <= 6:
            # Current week (slump week): 7 to 12 orders per day
            daily_order_count = random.randint(7, 12)
        elif 7 <= day_offset <= 13:
            # Prior week (peak promotion week): 22 to 28 orders per day
            daily_order_count = random.randint(22, 28)
        else:
            # Normal baseline: 11 to 16 orders per day
            daily_order_count = random.randint(11, 16)
            
        for _ in range(daily_order_count):
            # Pick customer
            if day_offset <= 60:
                # Inactive customers do not order in the last 60 days
                eligible_cids = [c["customer_id"] for c in customers 
                                 if c["customer_id"] not in inactive_customer_ids 
                                 and c["customer_id"] not in churn_risk_customer_ids]
            else:
                eligible_cids = [c["customer_id"] for c in customers]
                
            cid = random.choice(eligible_cids)
            
            # Select product
            # In the current slump week, high-end laptops were out of stock
            if 0 <= day_offset <= 6 and random.random() < 0.65:
                # Lower ticket items sold during slump week
                prod_choices = [p for p in PRODUCTS if p[2] in ["Accessories", "Headphones", "Smartwatches"]]
            else:
                prod_choices = PRODUCTS
                
            product = random.choice(prod_choices)
            pid, pname, pcat, pprice, pstock = product
            
            qty = random.choices([1, 2, 3], weights=[0.82, 0.14, 0.04])[0]
            amount = round(pprice * qty, 2)
            
            # Status: Completed (88%), Cancelled (6%), Returned (6%)
            status_rand = random.random()
            
            # In current week, cancellation rate was slightly higher (shipping delays)
            cancel_threshold = 0.11 if (0 <= day_offset <= 6) else 0.04
            
            # PRD-301 NovaSound ANC 700 has an unusually high return rate (15%)
            return_threshold = 0.15 if pid == "PRD-301" else 0.045
            
            if status_rand < cancel_threshold:
                status = "Cancelled"
                payment_status = "Refunded"
            elif status_rand < (cancel_threshold + return_threshold):
                status = "Returned"
                payment_status = "Refunded"
                
                # Create corresponding return record
                ret_id = f"RET-{return_counter}"
                return_counter += 1
                return_days_later = random.randint(1, 14)
                ret_date = (order_date + timedelta(days=return_days_later)).strftime("%Y-%m-%d")
                reason = get_weighted_return_reason(pid)
                
                returns.append({
                    "return_id": ret_id,
                    "order_id": f"ORD-{order_counter}",
                    "customer_id": cid,
                    "product_id": pid,
                    "product_name": pname,
                    "category": pcat,
                    "return_date": ret_date,
                    "reason": reason,
                    "refund_amount": amount
                })
            else:
                status = "Completed"
                payment_status = "Paid"
                
            oid = f"ORD-{order_counter}"
            order_counter += 1
            
            orders.append({
                "order_id": oid,
                "customer_id": cid,
                "product_id": pid,
                "product_name": pname,
                "category": pcat,
                "order_date": date_str,
                "quantity": qty,
                "unit_price": pprice,
                "amount": amount,
                "status": status,
                "payment_status": payment_status
            })
            
            # Update customer stats if completed or returned (transaction occurred)
            if status in ["Completed", "Returned"]:
                customer_stats[cid]["spent"] += amount
                customer_stats[cid]["orders"] += 1
                prev_last = customer_stats[cid]["last_date"]
                if not prev_last or order_date > prev_last:
                    customer_stats[cid]["last_date"] = order_date

    # 3. Update Customers with computed metrics & tiers
    for c in customers:
        cid = c["customer_id"]
        stats = customer_stats[cid]
        c["total_spent"] = round(stats["spent"], 2)
        c["total_orders"] = stats["orders"]
        if stats["last_date"]:
            c["last_order_date"] = stats["last_date"].strftime("%Y-%m-%d")
            days_inactive = (today - stats["last_date"]).days
            c["is_inactive"] = 1 if days_inactive >= 60 else 0
        else:
            c["last_order_date"] = "2026-05-01"
            c["is_inactive"] = 1
            
        # Determine tier
        spent = c["total_spent"]
        if spent >= 5000:
            c["customer_type"] = "Platinum"
        elif spent >= 2500:
            c["customer_type"] = "Gold"
        elif spent >= 1000:
            c["customer_type"] = "Silver"
        else:
            c["customer_type"] = "Standard"

    # Write CSV files
    # customers.csv
    with open(DATA_DIR / "customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(customers[0].keys()))
        writer.writeheader()
        writer.writerows(customers)
        
    # products.csv
    with open(DATA_DIR / "products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "price", "stock"])
        for p in PRODUCTS:
            writer.writerow(p)

    # orders.csv
    with open(DATA_DIR / "orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
        writer.writeheader()
        writer.writerows(orders)

    # returns.csv
    with open(DATA_DIR / "returns.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(returns[0].keys()))
        writer.writeheader()
        writer.writerows(returns)

    print(f"Generated {len(customers)} customers, {len(PRODUCTS)} products, {len(orders)} orders, {len(returns)} returns.")
    
    # 4. Seed SQLite Database
    seed_sqlite_db(customers, PRODUCTS, orders, returns)


def seed_sqlite_db(customers, products, orders, returns):
    print(f"Initializing SQLite database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("DROP TABLE IF EXISTS customers;")
    cur.execute("""
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        city TEXT,
        customer_type TEXT,
        total_orders INTEGER,
        total_spent REAL,
        last_order_date TEXT,
        is_inactive INTEGER
    );
    """)

    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute("""
    CREATE TABLE products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT,
        price REAL,
        stock INTEGER
    );
    """)

    cur.execute("DROP TABLE IF EXISTS orders;")
    cur.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        product_id TEXT,
        product_name TEXT,
        category TEXT,
        order_date TEXT,
        quantity INTEGER,
        unit_price REAL,
        amount REAL,
        status TEXT,
        payment_status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    cur.execute("DROP TABLE IF EXISTS returns;")
    cur.execute("""
    CREATE TABLE returns (
        return_id TEXT PRIMARY KEY,
        order_id TEXT,
        customer_id TEXT,
        product_id TEXT,
        product_name TEXT,
        category TEXT,
        return_date TEXT,
        reason TEXT,
        refund_amount REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """)

    cur.execute("DROP TABLE IF EXISTS policies;")
    cur.execute("""
    CREATE TABLE policies (
        policy_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        rule TEXT,
        approval_required INTEGER,
        conditions_json TEXT
    );
    """)

    # Insert data
    cur.executemany("""
    INSERT INTO customers VALUES (:customer_id, :name, :email, :phone, :city, :customer_type, :total_orders, :total_spent, :last_order_date, :is_inactive)
    """, customers)

    cur.executemany("""
    INSERT INTO products VALUES (?, ?, ?, ?, ?)
    """, products)

    cur.executemany("""
    INSERT INTO orders VALUES (:order_id, :customer_id, :product_id, :product_name, :category, :order_date, :quantity, :unit_price, :amount, :status, :payment_status)
    """, orders)

    cur.executemany("""
    INSERT INTO returns VALUES (:return_id, :order_id, :customer_id, :product_id, :product_name, :category, :return_date, :reason, :refund_amount)
    """, returns)

    # Insert policies from policies.json
    policies_path = DATA_DIR / "policies.json"
    if policies_path.exists():
        with open(policies_path, "r", encoding="utf-8") as f:
            policies_list = json.load(f)
            cur.executemany("""
            INSERT INTO policies VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (p["policy_id"], p["name"], p["category"], p["rule"], 1 if p.get("approval_required") else 0, json.dumps(p.get("conditions", {})))
                for p in policies_list
            ])

    # Create search indexes
    cur.execute("CREATE INDEX idx_orders_customer ON orders(customer_id);")
    cur.execute("CREATE INDEX idx_orders_product ON orders(product_id);")
    cur.execute("CREATE INDEX idx_orders_date ON orders(order_date);")
    cur.execute("CREATE INDEX idx_returns_product ON returns(product_id);")
    cur.execute("CREATE INDEX idx_customers_inactive ON customers(is_inactive);")

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    generate_all_data()
