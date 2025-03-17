from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__, static_folder="static")
CORS(app)

# ✅ Ensure Flask serves static files correctly
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ✅ Initialize Database
# ✅ Initialize Database
def init_db():
    with sqlite3.connect("tree.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            parent_id INTEGER,
                            left_child INTEGER,
                            right_child INTEGER,
                            active INTEGER DEFAULT 1,  -- ✅ Added active column (1 = Active, 0 = Inactive)
                            FOREIGN KEY (parent_id) REFERENCES users (id)
                          )''')
        conn.commit()


        

# ✅ Render HTML page
@app.route("/")
def home():
    return render_template("Kannivedi.html")

# ✅ Add new user to the tree
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data["name"].strip()
    parent_id = data.get("parent_id")

    with sqlite3.connect("tree.db") as conn:
        cursor = conn.cursor()

        if parent_id:
            cursor.execute("SELECT left_child, right_child FROM users WHERE id = ?", (parent_id,))
            parent = cursor.fetchone()
            if parent is None:
                return jsonify({"error": "Parent not found."}), 400
            if parent[0] and parent[1]:
                return jsonify({"error": "Parent already has two children."}), 400

            cursor.execute("INSERT INTO users (name, parent_id) VALUES (?, ?)", (name, parent_id))
            user_id = cursor.lastrowid
            if not parent[0]:
                cursor.execute("UPDATE users SET left_child = ? WHERE id = ?", (user_id, parent_id))
            else:
                cursor.execute("UPDATE users SET right_child = ? WHERE id = ?", (user_id, parent_id))
        else:
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))

        conn.commit()

    return jsonify({"message": "User added successfully."})

@app.route("/toggle_status", methods=["POST"])
def toggle_status():
    data = request.json
    user_id = data["id"]

    with sqlite3.connect("tree.db") as conn:
        cursor = conn.cursor()

        # ✅ Fetch current status
        cursor.execute("SELECT active FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        new_status = 0 if user[0] == 1 else 1  # Toggle between 1 (active) and 0 (inactive)

        # ✅ Update active status in the database
        cursor.execute("UPDATE users SET active = ? WHERE id = ?", (new_status, user_id))
        conn.commit()

    return jsonify({"message": "Status updated successfully!", "new_status": new_status})




# ✅ Edit user details
@app.route("/edit_user", methods=["POST"])
def edit_user():
    data = request.get_json()
    user_id = data["id"]
    new_name = data["name"].strip()

    with sqlite3.connect("tree.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
        conn.commit()

    return jsonify({"message": "User updated successfully."})

# ✅ Fetch tree data
@app.route("/get_tree", methods=["GET"])
def get_tree():
    with sqlite3.connect("tree.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id, left_child, right_child, active FROM users")
        users = {
            row[0]: {
                "id": row[0],
                "name": row[1],
                "parent": row[2],
                "left_child": row[3],
                "right_child": row[4],
                "active": row[5]  # ✅ Include active status
            }
            for row in cursor.fetchall()
        }
    return jsonify(users)


# ✅ Start Flask App
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
