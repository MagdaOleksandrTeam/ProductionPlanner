# 🏭 ProductionPlanner – Small Manufactory Management System

A comprehensive production planning and management system developed as a student project at **DSW University of Lower Silesia in Wrocław**.

## 👥 Authors & Roles

* **Magdalena Popczyk**:
    * **Lead UI/UX Designer**: Designed the visual identity and complete user experience.
    * **Frontend-to-Backend Integration**: Connected core logic with UI components across the entire system.
    * **Module Lead (Dashboard & Reporting)**: Developed the end-to-end logic, custom models, and interfaces for data analytics.
* **Oleksandr Horetskyi**:
    * **Backend & Logic Developer**: Designed the core engine and relational database architecture.
    * **Algorithm Engineering**: Implemented the **MRP-lite** engine and the greedy scheduling algorithm.
    * **UI Presentation Support**: Assisted in the visual representation of complex algorithmic outputs.

---

## 📝 Project Overview
The system was designed to automate production planning for small-scale manufacturing by integrating Bill of Materials (BOM), inventory tracking, and task scheduling.

---

## 🚀 Full System Features

### 📊 Dashboard & Analytics
* **Real-time KPI Monitoring**: Visual presentation of key performance indicators and production statistics.
* **Operational Overview**: Centralized view of current production status and resource availability.

### 📈 Reporting & Data Export
* **Multi-format Reports**: Generation of detailed production and material reports.
* **Data Portability**: Exporting system data to **CSV** or **PDF** files for external analysis or archiving.
* **Audit Readiness**: Professional data presentation for management and inventory control.

### 🛠️ Production & Material Management
* **BOM Management**: Comprehensive definition of product components and required quantities.
* **MRP-lite Engine**: Automated calculation of material requirements to prevent production delays.
* **Order Lifecycle**: End-to-end management of production orders with color-coded priority indicators (Red/Yellow/Green).

### 📅 Intelligent Scheduling
* **Automated Planning**: Use of a **greedy algorithm** to generate machine-specific schedules.
* **Gantt Chart Visualization**: Interactive timeline for tracking machine load and deadlines.

---

## 🛠️ Tech Stack
* **Language**: Python 3.12
* **GUI Framework**: PyQt6 (designed using Qt Designer)
* **Data Processing**: `pandas`, `numpy`
* **Visualization**: `matplotlib`
* **Database**: SQLite (Model 3NF – Third Normal Form)

---

## 📂 Architecture & Database Design
The application utilizes the **Repository Pattern** and **Singleton** pattern for robust database management.

### Database Integrity:
* **Normalization**: Data organized in **3NF** to eliminate redundancy.
* **Constraints**: Implementation of `FOREIGN KEY` (with `CASCADE` actions), `UNIQUE`, and `CHECK` constraints (e.g., `quantity > 0`).

---

## 🔒 Security & Validation (UI-Driven)
* **Input Sanitization**: Use of parameterized SQL queries to prevent injection attacks.
* **Validation Strategy**: UI-level constraints and specific input validators to ensure data consistency without unnecessary complexity.

---

## ⚙️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MagdaOleksandrTeam/ProductionPlanner.git
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Launch the application:
   ```bash
   python main.py
