# AI Lost & Found Intelligence Center — Advanced Project

## 1. Project Overview
**AI Lost & Found Intelligence Center (LFIC)** is an advanced desktop application for registering lost/found objects and ranking found-item images against a lost-item query image.

This version is structured as a small production-style Python project instead of a single monolithic script.

### Core capabilities
- Professional dashboard with live statistics
- Lost and Found item reporting
- Item description, location, date and contact information
- Safe image storage with duplicate filename handling
- SQLite database with automatic schema upgrade
- Hybrid visual matching:
  - ORB local feature matching — 75%
  - HSV color histogram similarity — 25%
- Top-5 ranked match candidates
- High / Medium / Low confidence labels
- Searchable records
- Active / Resolved workflow
- Right-click record management
- CSV report export
- Relative-path project design
- Windows one-click launcher with virtual environment

> **Important technical note:** the current engine is a computer-vision matching system, not a trained deep-learning classifier. Scores are ranking scores, not guaranteed probabilities.

## 2. Technology Stack
| Layer | Technology |
|---|---|
| Language | Python 3.10–3.13 recommended |
| GUI | Tkinter / ttk |
| Computer Vision | OpenCV |
| Image Processing | Pillow |
| Database | SQLite |
| Data Export | Python CSV |
| Architecture | Modular desktop application |

## 3. Project Architecture
```text
AI_Lost_Found_Intelligence_Center/
│
├── main.py                 # Application UI and workflows
├── database.py             # SQLite data layer and schema migration
├── matcher.py              # Hybrid image matching engine
├── requirements.txt        # Python dependencies
├── run_project.bat         # Windows automated launcher
├── README.md
│
├── data/
│   └── lost_found.db       # Runtime database (created automatically)
│
└── images/
    ├── lost/               # Uploaded lost-item images
    └── found/              # Uploaded found-item images
```

## 4. Installation
### Option A — easiest
Double-click `run_project.bat`.

### Option B — command line
```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## 5. Demonstration Workflow
1. Open **Report Found** and add several found items with images.
2. Open **Report Lost** and record the lost item.
3. Open **AI Match** and choose the lost-item image.
4. Click **RUN SMART MATCH**.
5. Review the top-ranked candidates.
6. Use **Records** to search reports or mark a case Resolved.
7. Use **Export CSV** to create an external report.

## 6. Matching Algorithm
The matcher combines two visual signals:

### ORB local features
ORB detects keypoints and descriptors that represent local visual structure. Candidate images are compared using Hamming-distance feature matching and a ratio test.

### HSV histogram
A two-dimensional Hue/Saturation histogram estimates overall color similarity. It helps when two photographs have similar colors but fewer repeatable local features.

### Final ranking score
```text
Final Score = (ORB Score × 0.75) + (Color Score × 0.25)
```

The application then ranks candidates from highest to lowest.

### Confidence bands
```text
70–100  → HIGH
45–69.99 → MEDIUM
0–44.99 → LOW
```

These bands are project heuristics and should not be interpreted as statistical confidence.

## 7. Database Design
The main `items` table stores:
- ID
- Item type
- Item name
- Description
- Location
- Date
- Contact
- Image path
- Status
- Created timestamp

The application automatically upgrades the database when older versions are detected.

## 8. Advanced Project Modules
### Dashboard
Provides total, lost, found, active and resolved counts.

### Reporting module
Validates required fields and dates, copies images into managed folders and creates database records.

### Matching module
Processes only active Found records and returns the five best candidates.

### Records module
Searches across item name, location, description and contact information. Records can be marked Active/Resolved or deleted.

### Reporting/export
Exports all records to a UTF-8 CSV file for Excel or further analysis.

## 9. Academic Project Objectives
This project demonstrates:
- Python GUI development
- Object-oriented programming
- File handling
- SQLite database management
- CRUD operations
- Computer vision
- Image feature extraction
- Similarity scoring
- Search/filter functionality
- Data export
- Modular software architecture
- Basic software engineering practices

## 10. Future Scope
For a true AI/ML production system, the ORB engine can later be replaced or combined with a pretrained deep-learning embedding model such as ResNet/EfficientNet/CLIP, followed by vector similarity search. Additional future modules could include:
- User authentication and roles
- Web/mobile client
- GPS/map-based location
- Email/SMS notifications
- Duplicate report detection
- Face/person privacy protection
- Cloud storage
- PostgreSQL/MySQL backend
- REST API
- Audit logs
- Admin analytics

## 11. Troubleshooting
### OpenCV installation error
```bat
python -m pip install --upgrade pip
python -m pip install opencv-python Pillow
```

### GUI does not open
Use a standard Python installation on Windows and run:
```bat
python main.py
```

### Old database compatibility
The application automatically creates/updates `data/lost_found.db`. If you need a completely clean test, close the application and delete that database.

## 12. Project Title for Submission
**AI-Based Lost & Found Intelligence Center Using Hybrid Image Feature Matching**

Suggested academic category:
**Advanced Python + Computer Vision + Database Management Project**
