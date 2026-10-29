# Lovnish - NIELIT ID Card Generator

An enterprise Django web portal for managing employees and students, featuring automated high-resolution ID card generation, dynamic text auto-fitting, embedded QR verification, interactive digital card previews, and print-ready multi-format exports (Word 3-Column Tables, A4 Sheets, CR80 PVC Plastic Badges, and RAW ZIP packs).

---

## 🚀 Key Features

- **Self-Service Registration Portal (`/`)**:
  - Employee and Student registration with instant photo upload and live course-branch cascading AJAX dropdowns.
  - Automatic background ID card rendering upon submission.
- **Interactive Digital ID Card Previews**:
  - Direct Front and Back card previews on both Employee (`/employee/<id>/`) and Student (`/student_detail/<enrollment>/`) pages.
  - Verified active status badges and click-to-zoom card inspections.
- **Searchable Directories**:
  - **Employee Directory (`/list/`)**: Search by name, employee ID, or designation with department filters.
  - **Student Directory (`/students/`)**: Search by name, enrollment number, or batch with course filters.
- **Multi-Format Export Engine**:
  - 📝 **Word Document (`.docx`)**: Lays out cards in an exact 3-column printing table grid (`[Back, Front, Back]`, `[Front, Back, Front]`) matching official NIELIT print requirements.
  - 📄 **Printable A4 Sheet (`.pdf`)**: 3-column batch sheet with outer cutting lines.
  - 💳 **Plastic Card PDF (CR80 PVC)**: Formatted to exact ISO standard card dimensions (54mm × 86mm).
  - 📦 **Raw Images (`.zip`)**: Download high-resolution front and back JPGs.
- **Dynamic Department & Template Administration**:
  - Manage departments (`Faculty`, `Guest Faculty`, `WBL`, etc.) and custom card background templates dynamically via Django Admin without modifying code.
- **Smart Text Auto-Fitting Engine**:
  - Dynamically calculates bounding boxes and scales down font sizes (from 20pt to 10pt) for long names, emails, and designations to prevent text overflow.
- **Embedded QR Code Verification**:
  - Embedded QR codes linking directly to the digital record for verification upon scan.
- **Production-Ready & WhiteNoise**:
  - Environment-based configuration (`.env`) for `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`.
  - Built-in WhiteNoise middleware for fast, self-hosted static asset delivery.
  - Branded custom `404.html` and `500.html` error pages.

---

## 🛠️ Tech Stack

- **Backend Framework**: Python 3.10+, Django 4.x / 5.x
- **Static Assets Serving**: WhiteNoise (`whitenoise`)
- **Document Generation**: `python-docx`, ReportLab (`reportlab`)
- **Image Processing**: OpenCV (`opencv-python`), Pillow (`PIL`)
- **QR Code Engine**: `qrcode`
- **Data Export**: `pandas`
- **Database**: SQLite3 (`db.sqlite3`) / PostgreSQL-ready

---

## 📁 Project Structure

```text
idcardnielit/
├── lovnish/                # Django project package (settings, urls, wsgi, asgi)
│   ├── settings.py         # Configured with .env support & WhiteNoise
│   └── urls.py             # Root routing and media handlers
├── myapp/                  # Core application
│   ├── Card/               # Card processing engine
│   │   ├── GenerateCard.py # Text auto-fitting & OpenCV/PIL rendering
│   │   ├── docx_generator.py # Word (.docx) 3-column table grid builder
│   │   └── pdf_generator.py  # ReportLab CR80 and A4 layout generator
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Global navigation & NIELIT footer
│   │   ├── register.html   # Dual Employee/Student registration form
│   │   ├── employee_list.html # Searchable employee directory
│   │   ├── student_list.html  # Searchable student directory
│   │   ├── employee_detail.html # Employee card preview & downloads
│   │   ├── student_detail.html  # Student card preview & downloads
│   │   ├── 404.html        # Custom 404 error page
│   │   └── 500.html        # Custom 500 error page
│   ├── admin.py            # ModelAdmin with bulk Word/PDF/ZIP actions
│   ├── models.py           # Department, Employee, Student, Course, Branch
│   ├── views.py            # Views for portal, APIs, and exports
│   └── forms.py            # ModelForms with dynamic department choices
├── media/                  # Uploaded profile photos
├── static/                 # Static assets (images, logos, fonts, CSS)
├── sample_data/            # Reference exports and CSV samples
├── .env.example            # Sample environment configuration template
├── db.sqlite3              # Pre-populated database with existing records
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

---

## ⚙️ Installation & Running

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/lovnishverma/idcardnielit.git
   cd idcardnielit
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment (Optional for local dev, Required for production)**:
   ```bash
   cp .env.example .env
   ```

4. **Run Database Migrations & Collect Static Files**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

5. **Start the Development Server**:
   ```bash
   python manage.py runserver 8000
   ```

6. **Core Portal URLs**:
   - **Registration**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Employee Directory**: [http://127.0.0.1:8000/list/](http://127.0.0.1:8000/list/)
   - **Student Directory**: [http://127.0.0.1:8000/students/](http://127.0.0.1:8000/students/)
   - **Admin Portal**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔑 Admin Credentials

- **URL**: `/admin/`
- **Username**: `computer name`
- **Password**: `***`

---

## 📄 License & Copyright

© 2027 NIELIT Chandigarh, Main Campus Ropar. All rights reserved.
