from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Keerthika@2005",
    database="plaDB"
)
cursor = db.cursor(dictionary=True)

# ----------------- HOME -----------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ----------------- PLANTS -----------------
@app.route('/plants')
def plants():
    cursor.execute("SELECT * FROM Plants")
    plants = cursor.fetchall()
    return render_template('plants.html', plants=plants)

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']
        cursor.execute("INSERT INTO Plants (Name, Category, Price, Stock) VALUES (%s, %s, %s, %s)",
                       (name, category, price, stock))
        db.commit()
        return redirect('/plants')
    return render_template('add_plant.html')

@app.route('/update_plant/<int:plant_id>', methods=['GET', 'POST'])
def update_plant(plant_id):
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']
        cursor.execute("UPDATE Plants SET Name=%s, Category=%s, Price=%s, Stock=%s WHERE PlantID=%s",
                       (name, category, price, stock, plant_id))
        db.commit()
        return redirect('/plants')

    cursor.execute("SELECT * FROM Plants WHERE PlantID = %s", (plant_id,))
    plant = cursor.fetchone()
    return render_template('update_plant.html', plant=plant)

@app.route('/delete_plant/<int:plant_id>')
def delete_plant(plant_id):
    try:
        # First, delete the associated order details
        cursor.execute("DELETE FROM Order_Details WHERE PlantID = %s", (plant_id,))
        db.commit()

        # Then, delete the plant itself
        cursor.execute("DELETE FROM Plants WHERE PlantID = %s", (plant_id,))
        db.commit()

    except mysql.connector.IntegrityError:
        return "Cannot delete plant: It is referenced in order details."
    
    return redirect('/plants')


# ----------------- CUSTOMERS -----------------
@app.route('/customers')
def customers():
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    return render_template('customers.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        cursor.execute("INSERT INTO Customers (Name, Email, Phone, Address) VALUES (%s, %s, %s, %s)",
                       (name, email, phone, address))
        db.commit()
        return redirect('/customers')
    return render_template('add_customer.html')

@app.route('/update_customer/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        cursor.execute("UPDATE Customers SET Name=%s, Email=%s, Phone=%s, Address=%s WHERE CustomerID=%s",
                       (name, email, phone, address, customer_id))
        db.commit()
        return redirect('/customers')

    cursor.execute("SELECT * FROM Customers WHERE CustomerID = %s", (customer_id,))
    customer = cursor.fetchone()
    return render_template('update_customer.html', customer=customer)

# ----------------- SUPPLIERS -----------------
@app.route('/suppliers')
def suppliers():
    cursor.execute("SELECT * FROM Suppliers")
    suppliers = cursor.fetchall()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']  # Correct key
        phone = request.form['phone']
        email = request.form['email']
        cursor.execute("INSERT INTO Suppliers (Name, Address, Phone, Email) VALUES (%s, %s, %s, %s)",
                       (name, address, phone, email))
        db.commit()
        return redirect('/suppliers')
    return render_template('add_supplier.html')

@app.route('/update_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def update_supplier(supplier_id):
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        cursor.execute("UPDATE Suppliers SET Name=%s, Address=%s, Phone=%s, Email=%s WHERE SupplierID=%s",
                       (name, address, phone, email, supplier_id))
        db.commit()
        return redirect('/suppliers')

    cursor.execute("SELECT * FROM Suppliers WHERE SupplierID = %s", (supplier_id,))
    supplier = cursor.fetchone()
    return render_template('update_supplier.html', supplier=supplier)

@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    try:
        cursor.execute("DELETE FROM Suppliers WHERE SupplierID = %s", (supplier_id,))
        db.commit()
    except mysql.connector.IntegrityError:
        return "Cannot delete supplier: It is referenced elsewhere."
    return redirect('/suppliers')

# ----------------- ORDERS & ORDER DETAILS -----------------
@app.route('/orders')
def orders():
    cursor.execute("""
        SELECT Orders.OrderID, Customers.Name AS CustomerName, Orders.OrderDate, Orders.TotalAmount
        FROM Orders JOIN Customers ON Orders.CustomerID = Customers.CustomerID
    """)
    orders = cursor.fetchall()
    return render_template('orders.html', orders=orders)

@app.route('/order_details')
def order_details():
    cursor.execute("SELECT OrderDetailID, OrderID, PlantID, Quantity, Subtotal FROM Order_Details")
    order_details = cursor.fetchall()
    return render_template('order_details.html', order_details=order_details)


@app.route('/take_order', methods=['GET', 'POST'])
def take_order():
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    cursor.execute("SELECT * FROM Plants")
    plants = cursor.fetchall()

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        selected_plants = request.form.getlist('plant_id')
        quantities = request.form.getlist('quantity')

        total_amount = 0
        order_details = []

        for plant_id, qty in zip(selected_plants, quantities):
            cursor.execute("SELECT Price FROM Plants WHERE PlantID = %s", (plant_id,))
            price = cursor.fetchone()['Price']
            qty = int(qty)
            subtotal = price * qty
            total_amount += subtotal
            order_details.append((plant_id, qty, subtotal))

        cursor.execute("INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES (%s, %s, %s)",
                       (customer_id, datetime.now().date(), total_amount))
        db.commit()
        order_id = cursor.lastrowid

        for plant_id, qty, subtotal in order_details:
            cursor.execute("INSERT INTO Order_Details (OrderID, PlantID, Quantity, Subtotal) VALUES (%s, %s, %s, %s)",
                           (order_id, plant_id, qty, subtotal))
        db.commit()

        return redirect('/orders')

    return render_template('take_order.html', customers=customers, plants=plants)

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
