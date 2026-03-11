# Database Documentation

## Overview

Schedulo uses PostgreSQL with SQLAlchemy ORM for data persistence.

## Database Schema

### Core Tables

#### users
- User accounts and profiles
- Stores timezone, role, contact info
- One-to-many: preferences, meetings

#### meetings
- Scheduled meetings
- Status: confirmed, pending, rescheduled, cancelled
- Priority: high, medium, low
- Type: team_sync, one_on_one, client_call, etc.

#### meeting_attendees
- Many-to-many relationship between meetings and users
- Tracks availability and response status

#### user_preferences
- User scheduling preferences
- Categories: time, behavior, priority, escalation
- Can be enabled/disabled

#### time_slots
- AI-recommended time slots
- Includes score, confidence, reasoning
- Stores conflicts and attendee availability

#### meeting_decisions
- AI decision explanations
- Links to recommended slot
- Stores agent insights and tradeoffs

### Supporting Tables

#### agent_activities
- Log of agent executions
- Real-time status tracking

#### schedule_requests
- History of scheduling requests
- Links to created meetings

#### calendar_events
- Cached external calendar data
- Synced from Google/Outlook

#### historical_meetings
- Aggregated meeting data for ML
- Used by behavior agent

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set database URL
export DATABASE_URL="postgresql://user:password@localhost/schedulo"

# Initialize database
python cli.py init

# Seed sample data
python cli.py seed
```

### Using CLI

```bash
# Initialize tables
python cli.py init

# Drop all tables
python cli.py drop

# Seed data
python cli.py seed

# Reset (drop + init + seed)
python cli.py reset
```

### Using Alembic Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

## Connection Management

### FastAPI Dependency

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Context Manager

```python
from database import get_db_context

with get_db_context() as db:
    user = db.query(User).filter_by(email="alex@schedulo.ai").first()
    print(user.name)
```

## Querying

### Basic Queries

```python
from database import get_db_context
from database.models import User, Meeting

with get_db_context() as db:
    # Get all users
    users = db.query(User).all()
    
    # Filter
    user = db.query(User).filter_by(email="alex@schedulo.ai").first()
    
    # Join
    meetings = db.query(Meeting).join(MeetingAttendee).filter(
        MeetingAttendee.user_id == "u1"
    ).all()
    
    # Order
    recent = db.query(Meeting).order_by(Meeting.start_time.desc()).limit(10).all()
```

### Relationships

```python
# User -> Preferences
user = db.query(User).first()
prefs = user.preferences  # Automatic join

# Meeting -> Attendees
meeting = db.query(Meeting).first()
attendees = meeting.attendees  # List of MeetingAttendee objects
```

## Seeding Data

Sample data is provided in `database/seed.py`:

- 5 users (Alex, Sarah, Marcus, Priya, James)
- 4 preferences for user u1
- 2 sample meetings

Customize by editing `seed.py` and running:
```bash
python cli.py seed
```

## Migrations

### Create Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add calendar_events table"

# Manual migration
alembic revision -m "Add index to meetings"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade
alembic downgrade -1
```

## Production Considerations

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Max additional connections
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True    # Verify connections before use
)
```

### Indexes

Key indexes for performance:
- `users.email` - User lookup
- `meetings.start_time` - Date range queries
- `meetings.status` - Status filtering
- `meeting_attendees.user_id` - User meetings
- `agent_activities.timestamp` - Recent activity

### Backups

**Render (Automatic):**
- Daily backups on paid plans
- Point-in-time recovery

**Manual:**
```bash
# Export
pg_dump $DATABASE_URL > backup.sql

# Import
psql $DATABASE_URL < backup.sql
```

## Environment Variables

```bash
# Development
DATABASE_URL=postgresql://localhost/schedulo_dev

# Production (Render)
DATABASE_URL=postgresql://user:pass@host:5432/schedulo

# Test
DATABASE_URL=postgresql://localhost/schedulo_test
```

## Testing

### Test Database

```python
# conftest.py
import pytest
from database import Base, engine

@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
```

### Factories

```python
# factories.py
from database.models import User

def create_user(**kwargs):
    defaults = {
        "id": "test_user",
        "name": "Test User",
        "email": "test@example.com",
        "timezone": "UTC"
    }
    defaults.update(kwargs)
    return User(**defaults)
```

## Troubleshooting

### Connection Errors

```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from database import engine; print(engine.connect())"
```

### Migration Conflicts

```bash
# View current revision
alembic current

# View pending migrations
alembic heads

# Resolve conflicts
alembic merge heads
```

### Performance Issues

```python
# Enable query logging
engine = create_engine(DATABASE_URL, echo=True)

# Use indexes
db.query(Meeting).filter(Meeting.start_time > date).all()

# Eager loading
db.query(Meeting).options(joinedload(Meeting.attendees)).all()
```

## Schema Diagram

```
users
  ├── user_preferences
  ├── meeting_attendees
  │     └── meetings
  │           ├── meeting_decisions
  │           └── time_slots
  ├── calendar_events
  └── historical_meetings

schedule_requests
agent_activities
```

## Best Practices

1. **Always use context managers or dependencies**
   ```python
   with get_db_context() as db:
       # Your code here
   ```

2. **Use transactions**
   ```python
   try:
       db.add(user)
       db.commit()
   except:
       db.rollback()
       raise
   ```

3. **Eager load relationships**
   ```python
   db.query(Meeting).options(joinedload(Meeting.attendees)).all()
   ```

4. **Use indexes for frequent queries**
   ```python
   __table_args__ = (Index('idx_email', 'email'),)
   ```

5. **Validate data with Pydantic**
   ```python
   from pydantic import BaseModel
   
   class UserCreate(BaseModel):
       email: EmailStr
       name: str
   ```
