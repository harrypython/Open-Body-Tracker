# Open Body Tracker - Functional Specification

**Version:** 1.0.0  
**Status:** Draft / MVP Definition  
**Target Audience:** Developers, Designers, Translators, and Open Source Contributors  

---

## 1. Product Vision & Principles

**Open Body Tracker** is an open-source, self-hosted application for tracking physical assessments, body composition, anthropometric measurements, and physical performance over time. 

It transforms raw assessment data into clear visual insights, progress milestones, comparisons, and reports. It is designed for personal trainers, nutritionists, physiotherapists, health clinics, and individuals tracking their own biometric data.

### Core Principles
1. **Data Sovereignty:** Users own their data. The system is self-hosted (via Docker), ensuring sensitive biometric data and photos never leave the user's infrastructure.
2. **Longitudinal Storytelling:** The primary value is not storing a single assessment, but visualizing evolution, trends, and milestones over months and years.
3. **Transparency:** All calculated metrics (e.g., Body Fat %, BMI, Fat Mass) must clearly state the protocol or formula used.
4. **Privacy-First:** Physical data is sensitive. The system enforces strict data isolation and provides easy tools for data export and deletion.
5. **Global Accessibility:** English-first interface, fully translatable via community-driven platforms like Weblate.

---

## 2. User Model & Access Control

The application adopts a **Single User Model**. There is only one user role focusing solely on self-tracking.

* **The "Member" Role:** Every user is a Member. 
* **Bootstrap:** Upon first installation via Docker, the setup wizard prompts the creation of the First Member.
* **User Creation:** Create and manage users via a secure login page.
* **Data Isolation:** Data is strictly siloed. Member A cannot view, edit, or delete Member B’s clients or assessments.
* **Account Deletion:** A Member can delete their own account and all associated data at any time.

---

## 3. Core Domain Concepts

| Concept | Description |
| :--- | :--- |
| **User** | A registered user of the system who manages their own assessments. |
| **Assessment** | A dated evaluation event containing multiple grouped measurements and optional photos. |
| **Protocol** | A scientific formula used to derive body composition metrics from raw skinfold measurements. |
| **Milestone** | An automatically detected notable achievement or personal record. |
| **Language Pack** | External JSON translation files managed via Weblate. |

---

## 4. Functional Modules

### 4.1. Onboarding & Workspace
* **First-Run Setup:** Initialize database, create the first Member account, and set default instance preferences.
* **User Management:** Create and manage users via a secure login page.
* **Dashboard Home:** A global view showing a list of the Member's Clients, recent assessments, and system alerts.

### 4.2. Client Management
**Individual Profile:** Basic static data (Name, Birth Date, Sex/Gender, Height, etc.) associated directly with the User account. This data represents the user being tracked.
* **Height Tracking:** Height is stored at the client level. If height changes, the historical record is preserved.
* **Status:** Clients can be marked as "Active" or "Archived" (hidden from main lists but data preserved).
* **Consent Record:** Optional field to log the date and terms of data processing consent (LGPD/GDPR awareness).

### 4.3. Assessment Management & Data Entry
The Assessment Wizard guides the user through grouped data entry. Fields are optional to support varied workflows.

* **General & Vitals:** Weight, Resting Heart Rate, Blood Pressure (Systolic/Diastolic), Mean Arterial Pressure (MAP).
* **Circumferences (Perimetry):** Right/Left Arms (relaxed & contracted), Forearms, Chest, Abdomen, Waist, Hip, Thighs, Calves.
* **Skinfolds (Adipometry):** Tricipital, Subscapular, Mid-Axillary, Suprailiac, Pectoral, Abdominal, Thigh, Bicipital.
* **Performance:** Abdominal repetitions, Isometric Plank duration.
* **Photos:** 
  * Upload up to 3 photos per assessment (Front, Side, Back).
  * Stored locally in a mapped Docker volume.
  * **Visual Timeline:** Gallery view of photos over time.
  * **Before/After Slider:** UI component to overlay and slide between the first and latest assessment photos.
* **Draft Mode:** Save incomplete assessments to finish later.
* **Quick Copy:** Pre-fill the new assessment form with data from the client's previous assessment.

### 4.4. Analytics & Insights
* **Trends (Time-Series Charts):** Interactive charts (via Recharts) for any metric. Support for date-range filtering, trend lines, and moving averages.
* **Comparison Engine:** Select any two assessments to view absolute and percentage variations side-by-side.
* **Milestones Engine:** Automatically detects and badges personal records (e.g., "Lowest Body Fat", "Longest Plank", "10kg Weight Loss").
* **Goals Tracker:** Define target metrics (e.g., "Reach 10% Body Fat") and track progress bars against the latest assessment.

### 4.5. Data Portability
* **CSV Export:** One-click export of all client data and assessments into a standardized CSV format.
* **CSV Import:** 
  * Downloadable CSV Template.
  * Import Wizard with data validation (checking date formats, numeric ranges) and duplicate detection.
  * Preview screen before committing data to the database.

### 4.6. Settings & Preferences
* **Unit System Toggle:** Users can switch between Metric (kg, cm, mm) and Imperial (lbs, in, ft). 
  * *Rule:* The database **always** stores Metric. The frontend handles conversion dynamically based on user preference.
* **Language Selection:** Switch interface language (powered by external JSON files).
* **Profile Management:** Update Member email, password, and display name.

---

## 5. Metric Catalog & Calculation Engine

The system supports a comprehensive catalog of metrics. Where applicable, the **Calculation Engine** derives values automatically.

### 5.1. Stored Metrics (Manual Entry)
* Weight, Heart Rate, Blood Pressure, Circumferences, Skinfolds, Performance Tests.

### 5.2. Calculated Metrics (Derived)
* **BMI & Classification:** Calculated from Weight and Height.
* **Waist-Hip Ratio (WHR):** Calculated from Waist and Hip circumferences.
* **Right/Left Averages & Asymmetry:** Calculated for bilateral measurements (Arms, Thighs, Calves).

### 5.3. Skinfold Protocol Engine
Instead of manually typing Body Fat %, the user enters the skinfold measurements (mm) and selects the protocol used. The system calculates:
1. **Body Density**
2. **Body Fat Percentage**
3. **Fat Mass (kg)**
4. **Lean Mass (kg)**

**Supported Initial Protocols:**
* Jackson & Pollock 7-site (Pectoral, Axillary, Tricipital, Subscapular, Abdominal, Suprailiac, Thigh)
* Pollock 3-site (Male/Female variations)
* Faulkner 
* Durnin & Womersley (4-site)

*Transparency Rule:* The UI will explicitly display: *"Body Fat: 9.5% (Calculated via Jackson & Pollock 7-site)"*. Users can override this and select "Manual Entry" if using a DEXA scan or smart scale.

---

## 6. Internationalization (i18n) Strategy

* **Source Language:** English (`en.json`).
* **Translation Platform:** Weblate integration.
* **File Format:** JSON (or Gettext `.po`), stored in the frontend `/locales` directory.
* **Workflow:** Developers add English keys to the source file. Weblate detects changes via webhook, community members translate via the Weblate UI, and translations are merged back via Pull Requests.
* **No Hardcoded Strings:** All UI text, tooltips, and error messages must use translation keys (e.g., `assessment.wizard.step1.title`).

---

## 7. User Journeys

### Journey 1: Initial Self-Tracking Assessment
1. User logs into their Open Body Tracker instance.
2. User initiates a "New Assessment" wizard.
3. User inputs skinfolds, selects "Jackson & Pollock 7-site," and uploads 3 progress photos.
4. System instantly calculates Body Fat %, Fat Mass, and Lean Mass based on the user's stored profile data.
5. User saves the assessment and views the newly populated Dashboard.

### Journey 2: The Household / Family Tracking
### Journey 2: Consistent Self-Tracking
1. User spins up the Docker container on their home server and registers their individual account.
2. User tracks their own metrics independently over time.
3. The system stores and presents a single, cohesive timeline of progress measurements.

### Journey 3: Migrating from Spreadsheets
### Journey 3: Migrating Historical Data from Spreadsheets (Single User)
1. User downloads the "Open Body Tracker CSV Template".
2. User copies their historical data from Excel into the template.
3. User uploads the CSV via the Import Wizard.
4. System validates the data, flags any missing skinfold values, and imports historical assessments.
5. User opens the Trends module and immediately sees a time-series chart of their evolution.

---

## 8. MVP Scope Definition

To ensure a successful initial open-source release, the MVP is strictly scoped.

### Must Have (v1.0)
* [ ] Docker Compose deployment (PostgreSQL, Backend, Frontend, Local Storage).
* [ ] Peer-to-Peer Member registration and Invitation system.
* [ ] Client Management (CRUD, Archiving).
* [ ] Assessment Wizard (Manual entry of all metric groups).
* [ ] Skinfold Protocol Engine (Auto-calculation of Body Fat/Mass).
* [ ] Photo Uploads & Visual Timeline.
* [ ] Dynamic Unit Toggle (Metric/Imperial UI conversion).
* [ ] Dashboard with Current Status & Variations.
* [ ] Time-series Charts for all metrics.
* [ ] Assessment Comparison Tool.
* [ ] Automatic Milestones & Personal Records.
* [ ] CSV Export & CSV Template Import.
* [ ] English-first UI with Weblate-ready JSON translation files.
* [ ] Anonymized Demo Data (based on standard longitudinal tracking).

### Should Have (v1.1)
* [ ] Goal Tracking (Target metrics and progress bars).
* [ ] Before/After Photo Overlay Slider.
* [ ] Printable / PDF Progress Reports.
* [ ] Advanced Chart Analytics (Moving averages, trend strength).
* [ ] Client Portal (Read-only view for the assessed individual).

### Won't Have (Out of Scope)
* [ ] Workout or Nutrition prescription (Focus remains strictly on assessment/tracking).
* [ ] Billing, payments, or gym management features.
* [ ] Medical diagnosis or clinical alerts.
* [ ] Native Mobile Apps (Web-responsive PWA approach preferred).
* [ ] Cloud-hosted SaaS version (Strictly self-hosted / open-source).

---

## 9. Non-Functional Requirements

1. **Deployment:** Must be deployable via a single `docker compose up -d` command.
2. **Storage:** Photos and database backups must be mapped to local Docker volumes to prevent data loss during container updates.
3. **Performance:** Dashboard and charts must load in under 2 seconds, even with 5+ years of historical assessment data.
4. **Security:** Passwords must be hashed (e.g., bcrypt/Argon2). API endpoints must enforce strict JWT-based data isolation (Members can only query their own `user_id` data).
5. **Accessibility:** Frontend must follow WCAG 2.1 AA guidelines (color contrast, keyboard navigation, screen reader support for charts).

***

### Next Steps for Development
With this functional specification locked in, the next logical steps for the repository are:
1. Initialize the Git repository and commit this `docs/functional-specification.md`.
2. Define the Database Schema (SQLAlchemy/Prisma models) based on the Metric Catalog.
3. Scaffold the FastAPI backend and React frontend structures.
4. Set up the Docker Compose environment.

Let me know if you want to proceed to the **Database Schema Design** or the **Project Folder Structure & Docker Compose setup** next!