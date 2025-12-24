import sqlite3
import os

DB_FILE = "commerce.db"

def seed_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    print(f"Creating database: {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create Tables (Schema)
    # A. Customers Table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT,
        signup_date DATE
    );
    """)

    # B. Suppliers Table
    cursor.execute("""
    CREATE TABLE suppliers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        contact_email TEXT,
        country TEXT
    );
    """)

    # C. Categories Table
    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    );
    """)

    # D. Products Table (Inventory)
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

    # E. Orders Table (Transactional Data)
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        total_amount DECIMAL(10, 2),
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );
    """)

    # F. Order Items Table (Many-to-Many between Orders and Products)
    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DECIMAL(10, 2),
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    # G. Reviews Table
    cursor.execute("""
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        customer_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        review_text TEXT,
        review_date DATE,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );
    """)

    # H. Payments Table
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

    # Insert Realistic Data
    print("Seeding data...")
    
    # Customers
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

    # Suppliers
    suppliers = [
        (1, 'TechCorp', 'contact@techcorp.com', 'USA'),
        (2, 'FurniWorld', 'info@furniworld.com', 'Canada'),
        (3, 'AccessoryHub', 'sales@accessoryhub.com', 'UK'),
    ]
    cursor.executemany("INSERT INTO suppliers VALUES (?,?,?,?)", suppliers)

    # Categories
    categories = [
        (1, 'Electronics', 'Electronic devices and gadgets'),
        (2, 'Furniture', 'Office and home furniture'),
        (3, 'Accessories', 'Various accessories'),
    ]
    cursor.executemany("INSERT INTO categories VALUES (?,?,?)", categories)

    # Products
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

    # Orders
    orders = [
        (1001, 1, '2024-01-10', 1250.00, 'completed'),
        (1002, 2, '2024-01-12', 150.00, 'completed'),
        (1003, 3, '2024-01-15', 1200.00, 'completed'),
        (1004, 4, '2024-01-20', 50.00, 'completed'),
        (1005, 5, '2024-02-01', 95.00, 'pending'),
    ]
    cursor.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)

    # Order Items
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

    # Reviews
    reviews = [
        (1, 101, 1, 5, 'Great laptop, fast and reliable!', '2024-01-15'),
        (2, 102, 1, 4, 'Good mouse, but battery life could be better.', '2024-01-16'),
        (3, 103, 2, 3, 'Chair is okay, but not very comfortable.', '2024-01-18'),
        (4, 105, 4, 5, 'Love the mugs, perfect for coffee!', '2024-01-25'),
    ]
    cursor.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?)", reviews)

    # Payments
    payments = [
        (1, 1001, 'Credit Card', '2024-01-10', 1250.00),
        (2, 1002, 'PayPal', '2024-01-12', 150.00),
        (3, 1003, 'Bank Transfer', '2024-01-15', 1200.00),
        (4, 1004, 'Credit Card', '2024-01-20', 50.00),
    ]
    cursor.executemany("INSERT INTO payments VALUES (?,?,?,?,?)", payments)

    conn.commit()
    conn.close()
    print("Database setup complete.")

    # Example Queries
    print("\nExample Queries to Test Feasibility:")
    print("1. Show all customers from USA.")
    print("2. List all products in the Electronics category.")
    print("3. Find orders placed by Alice Smith.")
    print("4. What is the total sales amount per product?")
    print("5. Show reviews for the Laptop Pro.")
    print("6. List suppliers and their countries.")
    print("7. Find customers who signed up in 2023.")
    print("8. Show pending orders.")
    print("9. What are the average ratings per category?")
    print("10. Find products with stock quantity less than 50.")

if __name__ == "__main__":
    seed_database()