# 🚀 Open Body Tracker - Project Plan & Development Roadmap

*Generated based on the Functional Specification (v1.0.0)*

This document outlines the phased approach for developing the Open Body Tracker application. It is designed to be a living document, refining the scope from MVP (v1.0) through planned feature additions (v1.1).

---

## 🎯 1. Project Goals & Principles

**Goal:** To create a secure, self-hosted, open-source platform for longitudinal tracking and visualization of anthropometric and physical assessment data for a single individual.

**Core Principles to Enforce:**
1.  **Data Sovereignty:** All data must be secured locally (Docker Compose).
2.  **Longitudinal Storytelling:** Focus on trend analysis, not single snapshots.
3.  **Privacy-First:** Robust data ownership and local encryption/storage practices for the individual user.
4.  **Transparency:** All calculated metrics must cite their formula/protocol.

---

## 🧱 2. Phase I: Foundations & Backend Development (The Engine)

*Focus: Establishing a secure data structure and reliable server-side logic.*

### 2.1. Database Schema Design (Schema/Models)
*   **Data Structure:** The system will use a multi-table, foreign key (FK) relationship model to ensure data integrity and i18n.
*   **Core Tables:**
    *   `User`: (Core account identity, holding static profile attributes like Name, Birth Date, Height, etc.).
    *   `Assessment`: (Dated evaluation event, storing measurements specific to the User ID).
    *   `Measurement`: (Actual measurement data, linking value to code and unit).
    *   `MetricCode` (CATALOG): (Contains the official metric key, allowing for flexibility and i18n).
    *   `UnitCode` (UNITS): (Will store and manage units. The `system_metric_unit` column defines the system's standard unit - **Metric**).
    *   `SkinfoldProtocol`: (Defines Jackson-Pollock 7-site).
    *   `Photo`: (Metadata for uploaded images, linking to local storage).

*   **Mandatory Logic Implementation:**
    *   **Conversion Layer:** A service layer that converts all incoming measurements to the system's standard unit (Metric).
    *   **Fixed Protocol:** The application will exclusively use the **Jackson & Pollock 7-site** protocol for all body composition calculations.
    *   **Calculations:** Implementation of complex, testable business logic for BMI, WHR, Averages (Rt/Lt), and the entire Body Fat % pipeline.

### 2.2. Core API Endpoints (FastAPI/Backend)
*   **Authentication & User:**
    *   `POST /api/v1/auth/register`: Handles single user registration (Self-Service).
    *   `POST /api/v1/auth/login`: JWT generation for the individual user.
*   **Assessment & Profile (Self-Service):**
    *   `GET /api/v1/user/profile`: Retrieves the current user's static profile data.
    *   `POST /api/v1/assessments/new`: Primary data submission endpoint. **(CRITICAL CONTRACT)**
    *   `GET /api/v1/assessments/history`: Retrieves the user's full assessment history for trend charting (Must load in <2s).
    *   `POST /api/v1/assessments/import`: Handles multi-record CSV data upload, validating against the current user profile.
*   **Data Portability:**
    *   `GET /api/v1/data/export`: Generates and streams the CSV data payload for the executing user.

---

## 🎨 3. Phase II: Frontend & User Experience (The Interface)

*Focus: Building an intuitive, responsive, and visually rich UI.*

### 3.1. Foundational Setup
*   **Tech Stack:** React/Vue + TypeScript.
*   **Component Library:** Headless UI (e.g., Radix) + Recharts.
*   **Internationalization:** Scaffolding `/locales` with keys (e.g., `assessment.wizard.step1.title`).

### 3.2. Module Implementation
*   **Dashboard (Home):**
    *   Overview: Quick stats for the individual user's overall status.
    *   Key Alerts: Missed assessments, outstanding tasks.
    *   Visualization: Simple summary graph (e.g., last 3 months' weight trend for the user).
*   **Individual Profile (The Self):**
    *   CRUD interface for the user's static personal data.
    *   Feature: Logging general user consent records.
*   **Assessment Wizard (The core flow):**
    *   Multi-step form controlled by state management.
    *   Validation: Real-time required field checks.
    *   **Protocol Engine UI:** Fixed Jackson & Pollock 7-site protocol selection.
    *   **Photo Handling:** Uploads + dedicated 'Before/After Slider' view focusing on the user's history.
*   **Analytics & Insights (Visualization Layer):**
    *   **Graphing Component:** Dedicated component for time-series data (supports date range filtering, moving averages).
    *   **Comparison View:** Side-by-side comparison component of the user's own historical assessments.
    *   **Milestones Engine:** Dedicated view showing automatically detected PRs (Personal Records) and milestones (e.g., "10kg lost").

---

## 🔬 4. Phase III: Quality Assurance, Deployment & Polish

### 4.1. Testing Strategy
*   **Goal:** Achieve high confidence in data integrity and security.
*   **Coverage:** Unit, Integration, and End-to-End (E2E) testing.
*   **Security:** Test authorization middleware (Verifying that the user can only access their own data by checking the `user_id` in all queries).

### 4.2. Deployment
*   **Docker Compose:** Finalize `docker-compose.yml` to manage:
    *   `db`: PostgreSQL (with persistent volume).
    *   `backend`: FastAPI/Python.
    *   `frontend`: React/Vue.
    *   `storage`: Mapping the photo volume.

---
