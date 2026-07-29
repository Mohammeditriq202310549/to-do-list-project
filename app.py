import re
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, insert, update, delete
from db import engine, users_table, todos_table, init_db

app = Flask(__name__)
app.secret_key = "super_secret_calendar_key"

# Ensure database tables exist
init_db()

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def is_valid_password(password):
    """
    Password Validation Rules:
    1. Minimum 8 characters
    2. At least 1 lowercase letter (a-z)
    3. At least 1 uppercase letter (A-Z)
    4. At least 1 symbol (!@#$%^&* etc.)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\\|/]", password):
        return False, "Password must contain at least one symbol (!@#$%^&*...)."
    return True, ""

@app.route("/")
def root():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            error = "Please enter both username and password."
        else:
            with engine.connect() as conn:
                stmt = select(users_table).where(users_table.c.email == email)
                user = conn.execute(stmt).fetchone()
                
                if not user:
                    error = "No account found with this username. Please register first."
                elif not check_password_hash(user.password, password):
                    error = "Invalid username or password."
                else:
                    session["logged_in"] = True
                    session["user_id"] = user.id
                    session["username"] = user.email
                    return redirect(url_for("index"))
                    
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            error = "Please enter both username and password."
        else:
            valid, msg = is_valid_password(password)
            if not valid:
                error = msg
            else:
                with engine.connect() as conn:
                    stmt = select(users_table).where(users_table.c.email == email)
                    existing = conn.execute(stmt).fetchone()
                    
                    if existing:
                        error = "Account already exists. Please login."
                    else:
                        hashed_pw = generate_password_hash(password)
                        ins = insert(users_table).values(
                            email=email,
                            password=hashed_pw,
                            name=email.split("@")[0]
                        )
                        res = conn.execute(ins)
                        conn.commit()
                        user_id = res.inserted_primary_key[0]
                        
                        session["logged_in"] = True
                        session["user_id"] = user_id
                        session["username"] = email
                        return redirect(url_for("index"))
                    
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    selected_month = request.args.get("month", "July")
    selected_day = request.args.get("day", "28")
    user_id = session.get("user_id")
    
    with engine.connect() as conn:
        stmt = select(todos_table).where(
            todos_table.c.month == selected_month,
            todos_table.c.day == selected_day
        )
        if user_id:
            stmt = stmt.where((todos_table.c.user_id == user_id) | (todos_table.c.user_id == None))
            
        result = conn.execute(stmt).mappings().all()
        
    todo_tasks = [dict(t, text=t['title']) for t in result if not t['completed']]
    done_tasks = [dict(t, text=t['title']) for t in result if t['completed']]
    
    days = [str(i) for i in range(1, 32)]
    
    return render_template(
        "index.html",
        months=MONTHS,
        days=days,
        selected_month=selected_month,
        selected_day=selected_day,
        todo_tasks=todo_tasks,
        done_tasks=done_tasks
    )

@app.route("/add", methods=["POST"])
def add_task():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    month = request.form.get("month", "July")
    day = request.form.get("day", "28")
    user_id = session.get("user_id")
    
    with engine.connect() as conn:
        stmt = select(todos_table).where(
            todos_table.c.month == month,
            todos_table.c.day == day
        )
        existing = conn.execute(stmt).all()
        count = len(existing)
        
        ins = insert(todos_table).values(
            user_id=user_id,
            title=f"Task {count + 1}",
            month=month,
            day=day,
            completed=False
        )
        conn.execute(ins)
        conn.commit()
        
    return redirect(url_for("index", month=month, day=day))

@app.route("/toggle", methods=["POST"])
@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    if task_id is None:
        task_id = int(request.form.get("task_id", 0))
        
    month = request.form.get("month", "July")
    day = request.form.get("day", "28")
    
    with engine.connect() as conn:
        stmt = select(todos_table).where(todos_table.c.id == task_id)
        task = conn.execute(stmt).fetchone()
        if task:
            new_status = not task.completed
            upd = update(todos_table).where(todos_table.c.id == task_id).values(completed=new_status)
            conn.execute(upd)
            conn.commit()
            
    return redirect(url_for("index", month=month, day=day))

@app.route("/edit", methods=["POST"])
@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    if task_id is None:
        task_id = int(request.form.get("task_id", 0))
        
    month = request.form.get("month", "July")
    day = request.form.get("day", "28")
    new_text = request.form.get("text", "")
    
    if new_text.strip():
        with engine.connect() as conn:
            upd = update(todos_table).where(todos_table.c.id == task_id).values(title=new_text)
            conn.execute(upd)
            conn.commit()
            
    return redirect(url_for("index", month=month, day=day))

@app.route("/delete", methods=["POST"])
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    if task_id is None:
        task_id = int(request.form.get("task_id", 0))
        
    month = request.form.get("month", "July")
    day = request.form.get("day", "28")
    
    with engine.connect() as conn:
        d = delete(todos_table).where(todos_table.c.id == task_id)
        conn.execute(d)
        conn.commit()
        
    return redirect(url_for("index", month=month, day=day))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
