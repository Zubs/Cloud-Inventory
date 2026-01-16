# Cloud Inventory Management System

A Flask-based Inventory Management System with MySQL database integration and AWS SNS notifications for low stock alerts.

## Features

- **Dashboard:** Real-time view of inventory, orders, and production status.
- **Management:** Add, Edit, and Delete items, orders, and users.
- **Alerts:** Automated email notifications via AWS SNS when stock drops below threshold.
- **Dockerized:** One-command setup for the entire stack.

## Prerequisites

- Docker & Docker Desktop
- AWS Account (for SNS alerts)

## Quick Start (Docker)

1. **Clone the repository**
```bash
git clone [https://github.com/Zubs/Cloud-Inventory.git](https://github.com/Zubs/Cloud-Inventory.git)
cd Cloud-Inventory
```

2. **Configure Environment:** Create a .env file in the root directory with your AWS credentials
```bash
cp env.example .env
```

3. **Run with Docker Compose:** This command builds the app and starts the database (automatically importing the schema).
```
docker-compose up --build
```

4. **Access the App:** Open http://localhost:5000 in your browser.

## Manual Setup (Without Docker)
1. Create a virtual environment: `python -m venv venv`

2. Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)

Install dependencies: `pip install -r requirements.txt`

Ensure you have a local MySQL server running and import `items.sql`.

Run the app: `flask --app main run`
