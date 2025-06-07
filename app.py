from flask import Flask, render_template, request, redirect, session, flash
import pyodbc
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=SHIVPRASAD\\SQLEXPRESS;'
                          'Database=model;'
                          'Trusted_Connection=yes;')
    return conn



# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['email'] = user[2]
                flash('Login successful!', 'success')
                return redirect('/profile')
            else:
                flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address = request.form['address']
        password = request.form['password']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Users (name, email, mobile_number, address, password) VALUES (?, ?, ?, ?, ?)',
                           (name, email, mobile_number, address, password))
            conn.commit()
            flash('Registered successfully! Please log in.', 'success')
            return redirect('/')
    return render_template('registration.html')


# Set the upload folder
UPLOAD_FOLDER = 'static/images'  # Specify your upload folder path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#
@app.route('/profile')
def profile():
    print("Session data:", session)
    if 'email' not in session:
        return redirect('/login')

    try:
        # Fetch user details
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE email = ?', (session['email'],))
            user = cursor.fetchone()

            if user is None:
                print("No user found for the provided email.")
                return redirect('/login')

            print(f"User details: {user}")

        # Fetch user's items
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Items WHERE user_id = ?', (user[0],))  # Assuming user_id is at index 0
            user_items = cursor.fetchall()

            print(f"User items: {user_items}")

        # Fetch all items
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    i.item_id, 
                    i.item_name, 
                    i.Inventory, 
                    i.price, 
                    i.image_path, 
                    u.name AS owner_name
                FROM Items i
                LEFT JOIN Users u ON i.user_id = u.user_id
                WHERE i.user_id = ?
            ''', (user[0],))
            items = cursor.fetchall()

            print(f"All items: {items}")

        return render_template('profile.html', user=user, user_items=user_items, items=items)

    except Exception as e:
        print(f"Detailed Error: {e}")
        return f"An error occurred while fetching your profile data: {e}", 500


# Add Item Page
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        Inventory = request.form['Inventory']
        price = request.form['price']
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)  # Sanitize the filename
                image_path = os.path.join(UPLOAD_FOLDER, filename)  # Store the path
                image.save(image_path)  # Save the file
        
        # Set a default image path if no image is uploaded
        if not image_path:
            image_path = os.path.join(UPLOAD_FOLDER, 'default_image.jpg')  # Replace with your default image name
        
        # Store only the relative path for the image in the database
        relative_image_path = image_path.replace('static/', '').replace('\\', '/')  # Store as 'images/filename.jpg'
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO items (item_name, Inventory, price, user_id, image_path) VALUES (?, ?, ?, ?, ?)',
                           (item_name, Inventory, price, session['user_id'], relative_image_path))
            conn.commit()
            flash('Item added successfully!', 'success')
            return redirect('/profile')
    
    return render_template('add_item.html')

@app.route('/update_inventory/<int:item_id>', methods=['POST'])
def update_inventory(item_id):
    if 'user_id' not in session:
        return redirect('/login')

    new_inventory = request.form.get('inventory')

    if not new_inventory:
        flash('Inventory cannot be empty.', 'danger')
        return redirect('/profile')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Items 
                SET Inventory = ? 
                WHERE item_id = ? AND user_id = ?''', 
                (new_inventory, item_id, session['user_id']))
            conn.commit()
        flash('Inventory updated successfully!', 'success')
    except Exception as e:
        print(f"Error updating inventory: {e}")
        flash('Failed to update inventory. Please try again.', 'danger')

    return redirect('/profile')


@app.route('/end_auction/<int:item_id>', methods=['POST'])
def end_auction(item_id):
    if 'user_id' not in session:
        return redirect('/login')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Delete the item from the database
            cursor.execute('DELETE FROM Items WHERE item_id = ?', (item_id,))
            conn.commit()

        flash('Item removed successfully!', 'success')
    except Exception as e:
        print(f"Error while ending auction: {e}")
        flash('Failed to remove item. Please try again.', 'danger')

    return redirect('/profile')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Logged out successfully.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)