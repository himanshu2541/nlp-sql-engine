import sqlite3
import os

# Define the directory for our databases
DB_DIR = "test_database"

def ensure_directory():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created directory: {DB_DIR}")

def get_db_path(db_name):
    return os.path.join(DB_DIR, db_name)

def clean_db(db_name):
    path = get_db_path(db_name)
    if os.path.exists(path):
        os.remove(path)
        print(f"Cleaned old database: {path}")

# ==========================================
# 1. CRM DATABASE (Customers & Reviews)
# ==========================================
def seed_crm_db():
    db_name = "crm.db"
    clean_db(db_name)
    
    print(f"Creating CRM database: {db_name}...")
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    # Table: Customers
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT,
        signup_date DATE
    );
    """)

    # Table: Reviews
    # Note: product_id refers to 'inventory.db', so we cannot enforce FK constraint here easily.
    # We keep customer_id FK since customers are in this DB.
    cursor.execute("""
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY,
        product_id INTEGER, 
        customer_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        review_text TEXT,
        review_date DATE,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );
    """)

    # Data: Customers
    customers = [
        (1, 'Alice Smith', 'alice@example.com', 'USA', '2023-01-15'),
        (2, 'Bob Jones', 'bob@example.com', 'UK', '2023-02-20'),
        (3, 'Charlie Brown', 'charlie@example.com', 'Canada', '2023-03-05'),
        (4, 'Diana Prince', 'diana@example.com', 'USA', '2023-04-10'),
        (5, 'Eve Wilson', 'eve@example.com', 'Australia', '2023-05-12'),
        (6, 'Frank Miller', 'frank@example.com', 'Germany', '2023-06-18'),
        (7, 'Grace Lee', 'grace@example.com', 'USA', '2023-07-22'),
        (8, 'Hank Green', 'hank@example.com', 'UK', '2023-08-30'),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    # Data: Reviews
    reviews = [
        (1, 101, 1, 5, 'Great laptop, fast and reliable!', '2024-01-15'),
        (2, 102, 1, 4, 'Good mouse, but battery life could be better.', '2024-01-16'),
        (3, 103, 2, 3, 'Chair is okay, but not very comfortable.', '2024-01-18'),
        (4, 105, 4, 5, 'Love the mugs, perfect for coffee!', '2024-01-25'),
    ]
    cursor.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?)", reviews)

    conn.commit()
    conn.close()

# ==========================================
# 2. INVENTORY DATABASE (Products, Categories, Suppliers)
# ==========================================
def seed_inventory_db():
    db_name = "inventory.db"
    clean_db(db_name)
    
    print(f"Creating Inventory database: {db_name}...")
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    # Table: Suppliers
    cursor.execute("""
    CREATE TABLE suppliers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        contact_email TEXT,
        country TEXT
    );
    """)

    # Table: Categories
    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    );
    """)

    # Table: Products
    # Both category_id and supplier_id are internal to this DB, so FKs are fine.
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        product_name TEXT,
        category_id INTEGER,
        supplier_id INTEGER,
        price DECIMAL(10, 2),
        stock_quantity INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    );
    """)

    # Data: Suppliers
    suppliers = [
        (1, 'TechCorp', 'contact@techcorp.com', 'USA'),
        (2, 'FurniWorld', 'info@furniworld.com', 'Canada'),
        (3, 'AccessoryHub', 'sales@accessoryhub.com', 'UK'),
    ]
    cursor.executemany("INSERT INTO suppliers VALUES (?,?,?,?)", suppliers)

    # Data: Categories
    categories = [
        (1, 'Electronics', 'Electronic devices and gadgets'),
        (2, 'Furniture', 'Office and home furniture'),
        (3, 'Accessories', 'Various accessories'),
    ]
    cursor.executemany("INSERT INTO categories VALUES (?,?,?)", categories)

    # Data: Products
    products = [
        (101, 'Laptop Pro', 1, 1, 1200.00, 50),
        (102, 'Wireless Mouse', 1, 1, 25.00, 200),
        (103, 'Office Chair', 2, 2, 150.00, 30),
        (104, 'Standing Desk', 2, 2, 450.00, 20),
        (105, 'Coffee Mug', 3, 3, 12.50, 500),
        (106, 'Bluetooth Headphones', 1, 1, 80.00, 100),
        (107, 'Notebook Set', 3, 3, 15.00, 300),
        (108, 'Ergonomic Keyboard', 1, 1, 60.00, 150),
    ]
    cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?,?)", products)

    conn.commit()
    conn.close()

# ==========================================
# 3. SALES DATABASE (Orders, Items, Payments)
# ==========================================
def seed_sales_db():
    db_name = "sales.db"
    clean_db(db_name)
    
    print(f"Creating Sales database: {db_name}...")
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    # Table: Orders
    # customer_id is external (in crm.db) -> No FK constraint
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, 
        order_date DATE,
        total_amount DECIMAL(10, 2),
        status TEXT DEFAULT 'pending'
    );
    """)

    # Table: Order Items
    # product_id is external (in inventory.db) -> No FK constraint
    # order_id is internal -> Keep FK
    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DECIMAL(10, 2),
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)

    # Table: Payments
    # order_id is internal -> Keep FK
    cursor.execute("""
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        payment_method TEXT,
        payment_date DATE,
        amount DECIMAL(10, 2),
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)

    # Data: Orders
    orders = [
        (1001, 1, '2024-01-10', 1250.00, 'completed'),
        (1002, 2, '2024-01-12', 150.00, 'completed'),
        (1003, 3, '2024-01-15', 1200.00, 'completed'),
        (1004, 4, '2024-01-20', 50.00, 'completed'),
        (1005, 5, '2024-02-01', 95.00, 'pending'),
    ]
    cursor.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)

    # Data: Order Items
    order_items = [
        (1, 1001, 101, 1, 1200.00),  # Laptop
        (2, 1001, 102, 2, 25.00),    # 2 Mice
        (3, 1002, 103, 1, 150.00),   # Chair
        (4, 1003, 101, 1, 1200.00),  # Laptop
        (5, 1004, 105, 4, 12.50),    # 4 Mugs
        (6, 1005, 106, 1, 80.00),    # Headphones
        (7, 1005, 107, 1, 15.00),    # Notebook
    ]
    cursor.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", order_items)

    # Data: Payments
    payments = [
        (1, 1001, 'Credit Card', '2024-01-10', 1250.00),
        (2, 1002, 'PayPal', '2024-01-12', 150.00),
        (3, 1003, 'Bank Transfer', '2024-01-15', 1200.00),
        (4, 1004, 'Credit Card', '2024-01-20', 50.00),
    ]
    cursor.executemany("INSERT INTO payments VALUES (?,?,?,?,?)", payments)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_directory()
    seed_crm_db()
    seed_inventory_db()
    seed_sales_db()
    print("\nAll databases seeded in 'test_database/' directory.")
    print("Update .env to point to these files:\n")
    print("DATABASES='{\"crm\": \"sqlite:///test_database/crm.db\", \"inventory\": \"sqlite:///test_database/inventory.db\", \"sales\": \"sqlite:///test_database/sales.db\"}'")