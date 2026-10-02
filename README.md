# 🐾 ASTA Adoption Center - Pet Adoption & Rescue Platform

**ASTA Adoption Center** is a full-featured web application and REST API built with **Django** and **Django REST Framework (DRF)**. It connects rescued animals (dogs, cats, birds, rabbits) across Bangladesh with loving homes. The application supports seamless pet browsing, multi-criteria filtering, online adoption requests, user dashboard tracking, and full admin moderation, with all pricing strictly standard in **BDT (৳)**.

---

## 🌟 Key Features

### 1. 👤 User Authentication & Management
- **Registration & Login**: Secure user sign up, login, and logout.
- **User Dashboard**: View profile details, track submitted adoption applications, and view saved favorite pets.

### 2. 🔍 Pet Browsing, Search & Filtering
- **Pet Listing**: Displays pet cards with image, species, breed, age, gender, location, status, and adoption fee in **BDT**.
- **Multi-Faceted Search & Filter**:
  - Filter by **Species** (Dog, Cat, Bird, Rabbit, Other)
  - Filter by **Gender** (Male, Female)
  - Search by **Keyword** (Name, Breed, Description)
  - Filter by **Location** (e.g. Dhaka, Chittagong, Sylhet, Rajshahi)
  - Filter by **Adoption Status** (Available, Adopted)
- **Pagination**: Supports page-based navigation (`1, 2, 3, Next`) in both frontend templates and REST API.

### 3. 🐾 Pet Details & Smart Adoption Flow
- Comprehensive pet profile with personality description, health/care info, location, and adoption fee (BDT).
- **Available Pets**: Logged-in users can click **[Apply for Adoption]** to open the adoption application form.
- **Adopted Pets**: If a pet has already been adopted, the page prominently displays:
  > **❌ This pet has already been adopted.**  
  *(Adoption button is disabled/hidden).*

### 4. 📝 Adoption Application
Users submit a dedicated application form with:
- Living Address (Bangladesh)
- Phone Number
- Why do you want this pet? (Reason)
- Have you owned a pet before? (Yes / No)
- Additional message (Optional)

### 5. 📋 User Dashboard ("My Adoption Requests")
- Real-time summary cards (Pending, Approved, Rejected).
- Clean table listing:
  - **Pet Name & Photo**
  - **Application Date & Time**
  - **Adoption Fee in BDT (৳)**
  - **Status Badge** (Pending, Approved, Rejected)
  - **Actions**: View pet profile or cancel pending application.

### 6. 🧠 Important Business Logic (Enforced in Models, Forms & API)
- **Rule 1 — Only Available Pets Can Be Adopted**:  
  If `pet.status == 'Adopted'`, new adoption applications are blocked.
- **Rule 2 — Prevention of Multiple Active Requests**:  
  A single user cannot submit multiple active (`Pending`) requests for the same pet.
- **Rule 3 — Application Approval & Pet Status Automation**:  
  When an admin approves an adoption application (`status = 'Approved'`), the pet's status automatically updates to `Adopted`.

### 7. ⭐ Bonus Features Implemented
- **❤️ Favorite Pets**: Users can save pets to their personal favorites and manage them from their dashboard or via the REST API.
- **📄 Template Pagination & API Pagination**: 6 pets per page with parameter preservation across filters.
- **🏷️ Pet Categories**: Dedicated filtering pills and species dropdown for Dogs, Cats, Birds, Rabbits, and Others.
- **🔐 Token Authentication**: API token generation and authorization for REST API clients.

---

## 🌐 REST API Endpoints (Django REST Framework)

Base URL: `/api/`

### 1. Pets API
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/pets/` | List pets with pagination, search, and filtering | Public |
| `GET` | `/api/pets/<id>/` | Retrieve specific pet details | Public |
| `POST` | `/api/pets/` | Create a new pet entry | Staff/Admin |
| `PUT` / `PATCH` | `/api/pets/<id>/` | Update pet details | Staff/Admin |
| `DELETE` | `/api/pets/<id>/` | Delete pet entry | Staff/Admin |

**Query Parameters for `/api/pets/`**:
- `?search=golden`
- `?animal_type=Dog`
- `?gender=Male`
- `?location=Dhaka`
- `?status=Available`
- `?page=2`

### 2. Adoption API
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/adoptions/` | List user's adoption requests (Staff sees all) | Authenticated |
| `POST` | `/api/adoptions/` | Submit a new adoption application | Authenticated |
| `GET` | `/api/adoptions/<id>/` | View adoption application details | Owner / Staff |
| `PUT` / `PATCH` | `/api/adoptions/<id>/` | Update request or status (Staff only for status) | Owner / Staff |

### 3. Bonus API Endpoints
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/favorites/` | List current user's favorite pets | Authenticated |
| `POST` | `/api/favorites/` | Add pet to favorites (or toggle) | Authenticated |
| `DELETE` | `/api/favorites/<pet_id>/` | Remove pet from favorites | Authenticated |
| `POST` | `/api/auth/register/` | Register new user via API and get Token | Public |
| `POST` | `/api/auth/login/` | Obtain auth token via credentials | Public |
| `GET` | `/api/auth/profile/` | Current user profile and counts | Authenticated |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14 / Django 6.1
- **API Framework**: Django REST Framework (DRF)
- **Filters**: django-filter
- **Image Processing**: Pillow
- **Frontend**: Django Templates, Vanilla CSS, Bootstrap 5.3, Bootstrap Icons
- **Database**: SQLite3 (default)
- **Currency**: BDT (`৳`)

---

## 🚀 Setup & Installation Instructions

### 1. Clone or Open the Repository
```bash
cd "ASTA Adoption Center"
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Demo Data (Optional but Recommended)
Populates pets, users, sample adoption requests, and generated photos:
```bash
python seed_db.py
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit the website at: **http://127.0.0.1:8000/**  
Django Admin Portal: **http://127.0.0.1:8000/admin/**  
REST API Root: **http://127.0.0.1:8000/api/pets/**

---

## 👥 Demo User Credentials

| Role | Username | Password | Notes |
|---|---|---|---|
| **Admin / Staff** | `admin` | `admin123` | Full access to Django Admin & API creation |
| **Demo User 1** | `rahim` | `password123` | Has Pending, Approved, and Rejected requests |
| **Demo User 2** | `fatima` | `password123` | Has adoption application for Bella |
| **Demo User 3** | `karim` | `password123` | Fresh user account |

---

## 🧪 Running Automated Tests

Run the complete test suite covering models, business rules, views, and DRF APIs:
```bash
python manage.py test
```
All 16 test cases validate:
- Pet model representation and availability properties
- Rule 1 (Only available pets can be adopted)
- Rule 2 (No duplicate active requests for the same pet)
- Rule 3 (Application approval updates pet status to Adopted)
- Search and filtering across categories and locations
- Adoption application submission flow
- DRF API CRUD operations, query filters, and token permissions
- Favorites toggle API

---

## 📁 Project Structure

```
ASTA Adoption Center/
├── asta_adoption/            # Django project configuration
│   ├── settings.py           # App settings, media/static config, DRF config
│   ├── urls.py               # Root URL dispatching
│   ├── wsgi.py
│   └── asgi.py
├── pets/                     # Main core application
│   ├── models.py             # Pet, AdoptionRequest, Favorite models
│   ├── admin.py              # Django admin configuration & actions
│   ├── forms.py              # UserRegisterForm, AdoptionApplicationForm, PetSearchFilterForm
│   ├── views.py              # Template-based UI views
│   ├── api_views.py          # DRF API views
│   ├── serializers.py        # DRF ModelSerializers
│   ├── urls.py               # Application & API routes
│   ├── context_processors.py # Global BDT currency & site settings
│   ├── tests.py              # 16 Unit & Integration tests
│   └── migrations/           # Database migration files
├── templates/                # HTML5 templates
│   ├── base.html             # Base layout with navbar and footer
│   └── pets/
│       ├── home.html         # Hero banner, stats, categories, featured pets
│       ├── pet_list.html     # Search, filter form, pet cards, pagination
│       ├── pet_detail.html   # Detailed pet view & adoption button
│       ├── adoption_form.html# Adoption application form
│       ├── dashboard.html    # User requests table & favorites
│       ├── login.html        # Login page
│       └── register.html     # Registration page
├── static/
│   └── css/
│       └── style.css         # Modern responsive styles & custom cards
├── media/pets/               # Uploaded pet photos
├── requirements.txt          # Python dependencies
├── seed_db.py                # Database population script
├── manage.py
└── README.md
```
