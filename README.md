# Mini-Wallet-App

Mini Wallet & Transaction API
A Django REST Framework-based API for managing user wallets and transactions, supporting multi-currency transfers with live exchange rates.

Features
    - User registration and JWT-based authentication
    - Wallet balance management (INR and USD)
    - Fund transfers with currency conversion using Frankfurter API
    - Transaction history with filtering

Prerequisites
    - Python 3.12
    - PostgreSQL
    - Git
  
## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wallet_api
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**:
   - Install PostgreSQL and create a database named `db_wallet_app`.
   - Example command:
     ```bash
     psql -U postgres -c "CREATE DATABASE db_wallet_app;"
     ```

5. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update `.env` with your PostgreSQL and Redis credentials:
     ```
     DB_HOST='localhost'
     DB_DATABASE='db_wallet_app'
     DB_USER=''
     DB_PASSWORD=''
     DB_PORT='5432'
     ```

6. **Apply migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access API documentation**:
   - Open `http://localhost:8000/api/` in a browser.


## API Endpoints
- **POST /api/register/**: Register a new user
- **POST /api/login/**: Obtain JWT token
- **GET /api/wallet/**: View wallet balance
- **POST /api/transfer/**: Transfer funds
- **GET /api/transactions/**: List transactions with filters