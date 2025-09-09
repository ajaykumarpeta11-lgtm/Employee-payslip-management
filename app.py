from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "payroll.db"

# --- Database Init ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dept TEXT,
            role TEXT,
            basic REAL,
            hra REAL,
            da REAL,
            pf REAL,
            gross REAL,
            net REAL
        )''')


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_salary(basic):
    hra = basic * 0.20
    da = basic * 0.10
    pf = basic * 0.05
    gross = basic + hra + da
    net = gross - pf
    return hra, da, pf, gross, net


@app.route("/")
def home():
    return render_template("index.html")


# --- Employees View with Password Every Time ---
@app.route("/employees", methods=["GET", "POST"])
def employees():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123":   # 🔑 password check
            conn = get_db_connection()
            employees = conn.execute("SELECT * FROM employees").fetchall()
            conn.close()
            return render_template("employees.html", employees=employees)
        else:
            return render_template("password.html", error="Invalid password!")

    # first time load: ask for password
    return render_template("password.html")


@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["dept"]
        role = request.form["role"]
        basic = float(request.form["basic"])

        hra, da, pf, gross, net = calculate_salary(basic)

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO employees (name, dept, role, basic, hra, da, pf, gross, net) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, dept, role, basic, hra, da, pf, gross, net)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("employees"))

    return render_template("add_employee.html")


@app.route("/delete/<int:id>")
def delete_employee(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("employees"))


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_employee(id):
    conn = get_db_connection()
    emp = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["dept"]
        role = request.form["role"]
        basic = float(request.form["basic"])

        hra, da, pf, gross, net = calculate_salary(basic)

        conn.execute(
            """UPDATE employees 
               SET name=?, dept=?, role=?, basic=?, hra=?, da=?, pf=?, gross=?, net=? 
               WHERE id=?""",
            (name, dept, role, basic, hra, da, pf, gross, net, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("employees"))

    conn.close()
    return render_template("update_employee.html", emp=emp)


# --- NEW: List all employees for payslip generation ---
@app.route("/payslips")
def payslips():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()
    return render_template("payslips.html", employees=employees)


# --- Single Payslip ---
@app.route("/payslip/<int:id>")
def payslip(id):
    conn = get_db_connection()
    emp = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("payslip.html", emp=emp)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
