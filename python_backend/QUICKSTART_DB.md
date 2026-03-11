# Database Quick Start

## Local Development

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE schedulo;

# Create user (optional)
CREATE USER schedulo_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE schedulo TO schedulo_user;

# Exit
\q
```

### 3. Configure Environment

```bash
cd python_backend

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://localhost/schedulo
# Or with user/password:
# DATABASE_URL=postgresql://schedulo_user:your_password@localhost/schedulo
API_V1_STR=/api
PROJECT_NAME=Schedulo
DEBUG=true
CORS_ORIGINS=http://localhost:5000,http://localhost:5173
EOF
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Create tables
python cli.py init

# Seed sample data
python cli.py seed
```

### 6. Start Backend

```bash
uvicorn main:app --reload --port 8000
```

## Using Docker (Alternative)

### 1. Start PostgreSQL Container

```bash
docker run --name schedulo-postgres \
  -e POSTGRES_DB=schedulo \
  -e POSTGRES_USER=schedulo_user \
  -e POSTGRES_PASSWORD=schedulo_pass \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Configure .env

```bash
DATABASE_URL=postgresql://schedulo_user:schedulo_pass@localhost:5432/schedulo
```

### 3. Initialize & Run

```bash
python cli.py init
python cli.py seed
uvicorn main:app --reload --port 8000
```

## CLI Commands

```bash
# Initialize database tables
python cli.py init

# Seed sample data
python cli.py seed

# Drop all tables (⚠️ destructive)
python cli.py drop

# Reset database (drop + init + seed)
python cli.py reset
```

## Verify Setup

```bash
# Check database connection
python -c "from database import engine; print(engine.connect())"

# Check tables
psql schedulo -c "\dt"

# Check data
psql schedulo -c "SELECT * FROM users;"
```

## Migrations (Advanced)

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Connection Refused

```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql
```

### Authentication Failed

```bash
# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Tables Not Created

```bash
# Run init command
python cli.py init

# Check for errors
python -c "from database import init_db; init_db()"
```

## Next Steps

1. ✅ Database running
2. ✅ Tables created
3. ✅ Sample data seeded
4. ✅ Backend connected

Now start the backend:
```bash
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/docs
