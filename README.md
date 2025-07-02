# UL Battery Research API

A Django REST Framework backend to process, analyze, and serve cycle-life data from UL's Electrochemical Safety Research Institute. This project provides a ranked summary of battery performance based on durability and resilience.

---

## Features

- Processes raw, multi-sheet Excel data for 21 battery cells.
- Calculates key performance metrics like State of Health (SOH) and overall averages.
- Implements a weighted ranking algorithm to score battery performance.
- Provides a clean, filterable REST API to serve the analyzed data.

---

## Technology Stack

- **Backend:** Django, Django REST Framework
- **Data Processing:** Pandas
- **Database:** SQLite (development)

---

## Getting Started

### Prerequisites

- Python 3.10+
- [Git LFS](https://git-lfs.com) (for pulling the data files)

### Local Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/TruLie13/BE-UL-Battery-Project.git
    cd BE-UL-Battery-Project
    ```

2.  **Pull LFS files:**

    ```bash
    git lfs install
    git lfs pull
    ```

3.  **Create and activate the virtual environment:**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Initialize and populate the database:**

    ```bash
    # Run migrations to create the database schema
    python manage.py migrate

    # Load all the data from the /data folder
    python manage.py load_battery_data
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/api/`.

---

## API Endpoints

- **`GET /api/summary/`**

  - Returns a summary of all batteries, ranked by a balanced performance score. Includes calculated metrics like SOH and overall averages.

- **`GET /api/batteries/<voltage_type>/`**

  - Returns a list of batteries for the specified `voltage_type` (`normal` or `reduced`). Includes detailed cycle-by-cycle data.

- **`GET /api/batteries/<voltage_type>/<battery_number>/`**
  - Returns the full detail for a single battery, including all cycle data.

---

## Data Source & Acknowledgements

This project uses open-source data provided by UL Research Institutes.

- **Original Data Source:** [UL-FRI Open Science Data](https://ul.org/institutes-offices/electrochemical-safety/open-science-data)
- **Specific Dataset:** Cycle Life Aging Test – Cylindrical Cell – Part 01 ([DOI: 10.5281/zenodo.7658812](https://doi.org/10.5281/zenodo.7658812))
