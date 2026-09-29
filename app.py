import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "bloodbank-secret-key-super-secure-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bloodbank.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================

# Preserved original Donor model (fully compatible with your original code)
class Donor(db.Model):
    __tablename__ = "donors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15))
    city = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User authentication model (Admin, Staff, Patient, Donor)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # admin, staff, patient, donor
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    blood_group = db.Column(db.String(5))
    city = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Blood Inventory Stock Table
class BloodStock(db.Model):
    __tablename__ = "blood_stock"
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), unique=True, nullable=False)
    units_available = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Patient Blood Requests
class BloodRequest(db.Model):
    __tablename__ = "blood_requests"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_requested = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.String(20), default="Normal") # Normal, Urgent, Critical
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default="Pending") # Pending, Approved, Rejected, Dispatched
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", backref="requests")

# Donor Donation Appointments / History
class DonationAppointment(db.Model):
    __tablename__ = "donation_appointments"
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    donor_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    appointment_date = db.Column(db.String(50), nullable=False)
    preferred_time = db.Column(db.String(20))
    center_location = db.Column(db.String(100), default="Central Blood Center")
    units = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="Pending") # Pending, Approved, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    donor = db.relationship("User", backref="appointments")


# ==========================================
# AUTH DECORATORS & HELPERS
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                flash("Access denied: You do not have permission to view that page.", "danger")
                return redirect(url_for("dashboard_dispatcher"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# PUBLIC & OVERVIEW ROUTES
# ==========================================

@app.route("/")
def index():
    """Overview / Landing Page with live blood bank stock metrics."""
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    stocks = {s.blood_group: s.units_available for s in BloodStock.query.all()}
    
    total_units = sum(stocks.values())
    total_donors = Donor.query.count() + User.query.filter_by(role="donor").count()
    total_requests = BloodRequest.query.count()
    urgent_requests = BloodRequest.query.filter(
        BloodRequest.urgency.in_(["Urgent", "Critical"]),
        BloodRequest.status == "Pending"
    ).all()

    return render_template(
        "overview.html",
        blood_groups=blood_groups,
        stocks=stocks,
        total_units=total_units,
        total_donors=total_donors,
        total_requests=total_requests,
        urgent_requests=urgent_requests
    )

# Upgraded Donor Directory (kept original route & behavior)
@app.route("/donors")
def donor_directory():
    group = request.args.get("group")
    if group:
        donors = Donor.query.filter_by(blood_group=group).all()
    else:
        donors = Donor.query.all()
    return render_template("index.html", donors=donors, selected_group=group)

# Preserved original /add route with upgrade
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        d = Donor(
            name=request.form.get("name", "").strip(),
            blood_group=request.form.get("blood_group", "O+"),
            phone=request.form.get("phone", "").strip(),
            city=request.form.get("city", "").strip()
        )
        db.session.add(d)
        db.session.commit()
        flash(f"Donor {d.name} successfully registered!", "success")
        return redirect(url_for("donor_directory"))
    return render_template("add.html")

# Preserved original /delete/<int:id> route
@app.route("/delete/<int:id>")
def delete(id):
    donor = Donor.query.get_or_404(id)
    name = donor.name
    db.session.delete(donor)
    db.session.commit()
    flash(f"Donor record for {name} removed.", "info")
    return redirect(url_for("donor_directory"))


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard_dispatcher"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["user_role"] = user.role
            session["full_name"] = user.full_name
            flash(f"Welcome back, {user.full_name}! ({user.role.title()})", "success")
            return redirect(url_for("dashboard_dispatcher"))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard_dispatcher"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "donor").lower()
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        blood_group = request.form.get("blood_group", "O+")
        city = request.form.get("city", "").strip()

        # Enforce self-registration only for donor & patient
        if role not in ["donor", "patient"]:
            role = "donor"

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another.", "warning")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            phone=phone,
            blood_group=blood_group,
            city=city
        )
        new_user.set_password(password)
        db.session.add(new_user)

        # If donor, also add to original donors table for search convenience
        if role == "donor":
            donor_entry = Donor(name=full_name, blood_group=blood_group, phone=phone, city=city)
            db.session.add(donor_entry)

        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("index"))


# ==========================================
# DASHBOARD ROUTER & INDIVIDUAL DASHBOARDS
# ==========================================

@app.route("/dashboard")
@login_required
def dashboard_dispatcher():
    role = session.get("user_role")
    if role == "admin":
        return redirect(url_for("dashboard_admin"))
    elif role == "staff":
        return redirect(url_for("dashboard_staff"))
    elif role == "patient":
        return redirect(url_for("dashboard_patient"))
    elif role == "donor":
        return redirect(url_for("dashboard_donor"))
    return redirect(url_for("index"))

# 1. ADMIN DASHBOARD
@app.route("/dashboard/admin")
@login_required
@role_required("admin")
def dashboard_admin():
    users = User.query.all()
    stocks = BloodStock.query.all()
    requests = BloodRequest.query.order_by(BloodRequest.request_date.desc()).limit(10).all()
    appointments = DonationAppointment.query.order_by(DonationAppointment.created_at.desc()).limit(10).all()
    
    total_users = len(users)
    total_staff = User.query.filter_by(role="staff").count()
    total_donors = User.query.filter_by(role="donor").count()
    total_patients = User.query.filter_by(role="patient").count()
    total_stock_units = sum(s.units_available for s in stocks)

    return render_template(
        "dashboard_admin.html",
        users=users,
        stocks=stocks,
        requests=requests,
        appointments=appointments,
        total_users=total_users,
        total_staff=total_staff,
        total_donors=total_donors,
        total_patients=total_patients,
        total_stock_units=total_stock_units
    )

# 2. STAFF DASHBOARD
@app.route("/dashboard/staff")
@login_required
@role_required("admin", "staff")
def dashboard_staff():
    stocks = BloodStock.query.all()
    pending_requests = BloodRequest.query.filter_by(status="Pending").order_by(BloodRequest.request_date.asc()).all()
    all_requests = BloodRequest.query.order_by(BloodRequest.request_date.desc()).limit(15).all()
    appointments = DonationAppointment.query.order_by(DonationAppointment.created_at.desc()).all()
    
    return render_template(
        "dashboard_staff.html",
        stocks=stocks,
        pending_requests=pending_requests,
        all_requests=all_requests,
        appointments=appointments
    )

# 3. DONOR DASHBOARD
@app.route("/dashboard/donor")
@login_required
@role_required("donor")
def dashboard_donor():
    user = User.query.get(session["user_id"])
    my_appointments = DonationAppointment.query.filter_by(donor_id=user.id).order_by(DonationAppointment.created_at.desc()).all()
    completed_donations = [a for a in my_appointments if a.status == "Completed"]
    
    return render_template(
        "dashboard_donor.html",
        user=user,
        appointments=my_appointments,
        completed_count=len(completed_donations)
    )

# 4. PATIENT DASHBOARD
@app.route("/dashboard/patient")
@login_required
@role_required("patient")
def dashboard_patient():
    user = User.query.get(session["user_id"])
    my_requests = BloodRequest.query.filter_by(patient_id=user.id).order_by(BloodRequest.request_date.desc()).all()
    available_stocks = {s.blood_group: s.units_available for s in BloodStock.query.all()}
    
    return render_template(
        "dashboard_patient.html",
        user=user,
        my_requests=my_requests,
        available_stocks=available_stocks
    )


# ==========================================
# ACTIONS: APPOINTMENTS, REQUESTS & INVENTORY
# ==========================================

# Donor Books Donation Appointment
@app.route("/donor/book-appointment", methods=["POST"])
@login_required
@role_required("donor")
def book_appointment():
    user = User.query.get(session["user_id"])
    appt_date = request.form.get("appointment_date")
    preferred_time = request.form.get("preferred_time")
    center = request.form.get("center_location", "Central Blood Center")
    
    appt = DonationAppointment(
        donor_id=user.id,
        donor_name=user.full_name,
        blood_group=user.blood_group or "O+",
        appointment_date=appt_date,
        preferred_time=preferred_time,
        center_location=center,
        status="Pending"
    )
    db.session.add(appt)
    db.session.commit()
    flash("Donation appointment scheduled! Our staff will review and confirm it.", "success")
    return redirect(url_for("dashboard_donor"))

# Patient Submits Blood Request
@app.route("/patient/request-blood", methods=["POST"])
@login_required
@role_required("patient")
def submit_blood_request():
    user = User.query.get(session["user_id"])
    hospital = request.form.get("hospital_name", "").strip()
    blood_group = request.form.get("blood_group")
    units = int(request.form.get("units_requested", 1))
    urgency = request.form.get("urgency", "Normal")
    reason = request.form.get("reason", "").strip()

    req = BloodRequest(
        patient_id=user.id,
        patient_name=user.full_name,
        hospital_name=hospital,
        blood_group=blood_group,
        units_requested=units,
        urgency=urgency,
        reason=reason,
        status="Pending"
    )
    db.session.add(req)
    db.session.commit()
    flash(f"Blood request for {units} unit(s) of {blood_group} submitted successfully.", "success")
    return redirect(url_for("dashboard_patient"))

# Staff/Admin Updates Blood Stock Directly
@app.route("/stock/update", methods=["POST"])
@login_required
@role_required("admin", "staff")
def update_stock():
    blood_group = request.form.get("blood_group")
    delta = int(request.form.get("delta", 0))
    
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    if stock:
        new_val = stock.units_available + delta
        if new_val < 0:
            flash(f"Cannot reduce stock below 0! Current units for {blood_group}: {stock.units_available}", "danger")
        else:
            stock.units_available = new_val
            db.session.commit()
            flash(f"Updated {blood_group} stock by {delta:+d} units (New total: {new_val}).", "success")
    
    if session.get("user_role") == "admin":
        return redirect(url_for("dashboard_admin"))
    return redirect(url_for("dashboard_staff"))

# Staff/Admin Processes Patient Request (Approve/Reject/Dispatch)
@app.route("/request/status/<int:req_id>/<string:new_status>")
@login_required
@role_required("admin", "staff")
def change_request_status(req_id, new_status):
    req = BloodRequest.query.get_or_404(req_id)
    valid_statuses = ["Approved", "Rejected", "Dispatched"]
    
    if new_status in valid_statuses:
        # If approving or dispatching, check if stock exists
        if new_status == "Approved" and req.status == "Pending":
            stock = BloodStock.query.filter_by(blood_group=req.blood_group).first()
            if not stock or stock.units_available < req.units_requested:
                flash(f"Cannot approve: Insufficient {req.blood_group} stock ({stock.units_available if stock else 0} available, {req.units_requested} required).", "danger")
                return redirect(url_for("dashboard_staff"))
            # Deduct stock on approval
            stock.units_available -= req.units_requested
        
        req.status = new_status
        db.session.commit()
        flash(f"Request #{req.id} marked as '{new_status}'.", "info")
    
    return redirect(url_for("dashboard_staff"))

# Staff/Admin Updates Donation Appointment Status (Approved / Completed)
@app.route("/appointment/status/<int:appt_id>/<string:new_status>")
@login_required
@role_required("admin", "staff")
def change_appointment_status(appt_id, new_status):
    appt = DonationAppointment.query.get_or_404(appt_id)
    if new_status in ["Approved", "Completed", "Cancelled"]:
        # If marked completed, add 1 unit to stock!
        if new_status == "Completed" and appt.status != "Completed":
            stock = BloodStock.query.filter_by(blood_group=appt.blood_group).first()
            if stock:
                stock.units_available += appt.units
                flash(f"Donation verified! Added {appt.units} unit of {appt.blood_group} to blood bank stock.", "success")
        
        appt.status = new_status
        db.session.commit()
        flash(f"Appointment #{appt.id} status updated to {new_status}.", "info")

    return redirect(url_for("dashboard_staff"))

# Admin Creates New Staff or Admin Account
@app.route("/admin/create-user", methods=["POST"])
@login_required
@role_required("admin")
def admin_create_user():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "staff").lower()
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash("Username or Email already exists!", "danger")
        return redirect(url_for("dashboard_admin"))

    new_user = User(
        username=username,
        email=email,
        role=role,
        full_name=full_name,
        phone=phone
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash(f"Successfully created new {role.title()} user: {username}", "success")
    return redirect(url_for("dashboard_admin"))


# ==========================================
# SEED DATABASE INITIALIZER
# ==========================================

def seed_database():
    """Initializes tables and seeds default blood stocks and sample demo accounts."""
    db.create_all()

    # 1. Initialize 8 blood groups stock if empty
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    default_stock = {
        "A+": 18, "A-": 8, "B+": 25, "B-": 6,
        "AB+": 9, "AB-": 3, "O+": 32, "O-": 12
    }
    for group in blood_groups:
        if not BloodStock.query.filter_by(blood_group=group).first():
            db.session.add(BloodStock(blood_group=group, units_available=default_stock[group]))

    # 2. Seed default users for all 4 roles if they don't exist
    demo_users = [
        ("admin", "admin@bloodbank.org", "admin123", "admin", "Dr. Alexander Wright", "555-0101", "O+"),
        ("staff", "staff@bloodbank.org", "staff123", "staff", "Nurse Sarah Jenkins", "555-0102", "A+"),
        ("donor", "donor@bloodbank.org", "donor123", "donor", "Johnathon Miller", "555-0103", "O+"),
        ("patient", "patient@bloodbank.org", "patient123", "patient", "Emily Watson", "555-0104", "B-")
    ]

    for uname, email, pwd, role, name, phone, bg in demo_users:
        if not User.query.filter_by(username=uname).first():
            u = User(username=uname, email=email, role=role, full_name=name, phone=phone, blood_group=bg, city="Metropolis")
            u.set_password(pwd)
            db.session.add(u)

    # 3. Seed sample Donors for legacy index page
    if Donor.query.count() == 0:
        sample_donors = [
            Donor(name="Johnathon Miller", blood_group="O+", phone="555-0103", city="Metropolis"),
            Donor(name="Rebecca Hall", blood_group="A+", phone="555-0112", city="Gotham"),
            Donor(name="Marcus Chen", blood_group="B-", phone="555-0134", city="Star City"),
            Donor(name="David Miller", blood_group="AB+", phone="555-0178", city="Central City"),
            Donor(name="Sophia Turner", blood_group="O-", phone="555-0199", city="Metropolis")
        ]
        db.session.bulk_save_objects(sample_donors)

    # 4. Seed sample Blood Request
    if BloodRequest.query.count() == 0:
        patient_user = User.query.filter_by(username="patient").first()
        if patient_user:
            req1 = BloodRequest(
                patient_id=patient_user.id,
                patient_name=patient_user.full_name,
                hospital_name="City General Hospital - Trauma ICU",
                blood_group="B-",
                units_requested=2,
                urgency="Critical",
                reason="Emergency scheduled surgical procedure",
                status="Pending"
            )
            req2 = BloodRequest(
                patient_id=patient_user.id,
                patient_name=patient_user.full_name,
                hospital_name="St. Jude Memorial",
                blood_group="O+",
                units_requested=1,
                urgency="Normal",
                reason="Post-operative blood transfusion",
                status="Approved"
            )
            db.session.add_all([req1, req2])

    # 5. Seed sample Donation Appointment
    if DonationAppointment.query.count() == 0:
        donor_user = User.query.filter_by(username="donor").first()
        if donor_user:
            appt = DonationAppointment(
                donor_id=donor_user.id,
                donor_name=donor_user.full_name,
                blood_group="O+",
                appointment_date="2026-10-05",
                preferred_time="10:30 AM",
                center_location="Central Blood Center - Main Hall",
                units=1,
                status="Pending"
            )
            db.session.add(appt)

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        seed_database()
    print("\n" + "="*60)
    print("🩸 Blood Bank Management System Upgraded Successfully!")
    print("🌐 Running at: http://127.0.0.1:5000")
    print("="*60)
    print("🔑 Demo Accounts:")
    print("   👑 Admin:   username: admin   | password: admin123")
    print("   🩺 Staff:   username: staff   | password: staff123")
    print("   🩸 Donor:   username: donor   | password: donor123")
    print("   🏥 Patient: username: patient | password: patient123")
    print("="*60 + "\n")
    app.run(debug=True)
