# 🩸 BloodBank Connect - Full-Stack Blood Management System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

A web-based **Blood Bank Management System** built with **Python (Flask)**, **SQLAlchemy**, and **Bootstrap 5**. The portal coordinates life-saving operations across four distinct user roles: **Administrators**, **Hospital / Bank Staff**, **Voluntary Donors**, and **Patients**.

---

## 🌟 Key Features

### 1. 🌐 Public Real-Time Blood Stock & Overview
* **Live Inventory Grid**: Publicly displays units available for all 8 blood types (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`).
* **Stock Health Indicators**: Automated status badges (*Optimal*, *Moderate*, *Critical Low*).
* **Urgent Requisition Alert**: Real-time ticker highlighting critical hospital needs.

### 2. 🔐 Multi-Role Authentication & Access Control
* Secure session-based authentication with password hashing via `werkzeug.security`.
* Dedicated permissions and tailored dashboards for each role.

### 3. 👥 4 Specialized Dashboards

| Role | Key Capabilities |
| :--- | :--- |
| 👑 **Administrator** | Overall system analytics, user account directory, staff creation, inventory overview. |
| 🩺 **Staff / Nurse** | Dynamic stock adjustment (`+` / `-`), review & approve patient requests (auto-deducts stock), verify donor appointments (auto-adds stock). |
| 🩸 **Donor** | Digital Donor ID Card, schedule blood donation appointments, track donation history, review health eligibility checklist. |
| 🏥 **Patient / Requester** | Submit hospital blood requisitions with urgency level (*Normal*, *Urgent*, *Critical*), track live fulfillment status (*Pending*, *Approved*, *Dispatched*, *Rejected*). |

---

## 🛠️ Tech Stack

* **Backend**: Python 3, Flask
* **Database & ORM**: SQLite3, Flask-SQLAlchemy
* **Frontend**: HTML5, Jinja2 Templates, Bootstrap 5.3, FontAwesome 6, Google Fonts (Plus Jakarta Sans)
* **Security**: Werkzeug password hashing, session-based route guards

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher installed on your system.

### Installation & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bloodbank_project.git
   cd bloodbank_project
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python app.py
   ```

5. **Access in browser:**
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Pre-Configured Demo Credentials

The database automatically seeds on initial run with demo accounts:

| Role | Username | Password |
| :--- | :--- | :--- |
| 👑 **Admin** | `admin` | `admin123` |
| 🩺 **Staff** | `staff` | `staff123` |
| 🩸 **Donor** | `donor` | `donor123` |
| 🏥 **Patient** | `patient` | `patient123` |

*(Quick-fill shortcut buttons are provided on the login page for 1-click testing).*

---

## 📁 Project Structure

```
bloodbank_project/
│
├── app.py                      # Application entry point, DB models & controller routes
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # Comprehensive project documentation
│
└── templates/                  # Frontend Jinja2 templates
    ├── base.html               # Master layout with responsive navbar & alerts
    ├── overview.html           # Public landing page with live stock metrics
    ├── login.html              # Sign-in portal with 1-click demo autofill
    ├── register.html           # User registration (Donor / Patient)
    ├── dashboard_admin.html    # Administrator command center
    ├── dashboard_staff.html    # Staff operations desk
    ├── dashboard_donor.html    # Donor personal hub & digital donor card
    ├── dashboard_patient.html  # Patient requisition & live status tracker
    ├── index.html              # Public donor directory
    └── add.html                # Register donor form
```

---

## 📄 License
This project is licensed under the MIT License - feel free to use and modify it for your projects!
