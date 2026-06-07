# Atlas Shared App

Shared database entities, services, and APIs for the Atlas project. This library provides:
- SQLModel-based entity definitions for cases, users, and clients
- Repository layer for database operations
- Service layer for business logic
- FastAPI route definitions for REST APIs

**Important:** Only use `table=True` if the table is meant to be created for all applications (like case, etc.). Application-specific tables should be defined in their respective application repositories.

### Examples

**Case entities** are meant for all applications (those will be created as db table with alembic_autoddl):
```python
class Case(CaseBase, AtlasBaseModel, table=True):
    pass
```

**User entities** are only for `atlas-app-identity`:
```python
# leave this table to atlas-app-identity
class User(UserBase, AtlasBaseModel, table=False):
    pass
```

**User entities** in `atlas-app-identity` (re-create the entity to create table):
```python
from atlas_shared_app import User as UserTable

class User(UserTable, table=True):
    pass
```



## Installation

```bash
pip install atlas-shared-app
```

Or install from source:

```bash
git clone https://github.com/yourusername/atlas-shared-app.git
cd atlas-shared-app
pip install -e .
```

## Requirements

- Python >= 3.8
- SQLModel 0.0.27
- Pydantic 2.12.5
- SQLAlchemy 2.0.45

## Quick Start

### Running the Example Application

1. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

2. Run the application:
```bash
# Install dependencies
pip install -e .

# Run the example app
python -m atlas_shared_app.app
```

3. Access the API:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Case APIs: http://localhost:8000/cases/v1/
- Config APIs: http://localhost:8000/configs/v1/

## Usage

## Inherited Class Order and Column Order

The sequence of inherited classes matters for adjusting the table column order. The **last inherited class defines columns that appear first** in the table.

```python
class AtlasCase(AtlasBaseModel, AtlasCaseBase, AtlasCasePrimaryKey, table=True):
    pass
```

In this example:
- Columns from `AtlasCasePrimaryKey` appear **first** in the table (last in inheritance)
- Columns from `AtlasCaseBase` appear **second**
- Columns from `AtlasBaseModel` appear **last** (first in inheritance)

This is because Python's Method Resolution Order (MRO) processes classes from right to left, and SQLModel collects fields in that order.

### Importing Entities

```python
from atlas_shared_app import (
    Case,
    CaseStatus,
    CaseConfig,
    CaseDocument,
    CaseHistory,
    CaseRemark,
    User,
    Client,
)
```

### Using Case Entities

```python
from atlas_shared_app import Case, CaseStatus

# Create a new case
case = Case(
    title="Customer Support Inquiry",
    status=CaseStatus.OPEN,
    client_id=1,
    assigned_user_id=2
)
```

### Using User Entity

```python
from atlas_shared_app import User

# Create a new user
user = User(
    name="John Doe",
    email="john@example.com"
)
```

### Using Client Entity

```python
from atlas_shared_app import Client

# Create a new client
client = Client(
    name="Acme Corporation",
    contact_email="contact@acme.com"
)
```

### Using APIs

The library includes a reference FastAPI application (`atlas_shared_app/app.py`) that demonstrates how to register and use the APIs:

```bash
# Run the example application
python -m atlas_shared_app.app

# Or use uvicorn directly
uvicorn atlas_shared_app.app:app --reload
```

**Create your own application:**

```python
from fastapi import FastAPI
from atlas_shared_app import register_case_apis, register_case_config_apis

app = FastAPI()

# Define your database engine function
async def get_engine():
    return your_async_engine

# Register the APIs
register_case_apis(app, get_engine)
register_case_config_apis(app, get_engine)
```

See the [APIs README](atlas_shared_app/apis/README.md) for detailed API documentation and the `example_custom_app.py` file for a complete integration example with authentication.

## Module Structure

```
atlas_shared_app/
├── case/             # Case-related entities
│   ├── case.py
│   ├── case_config.py
│   ├── case_document.py
│   ├── case_history.py
│   └── case_remark.py
├── user/             # User entities
│   └── user.py
├── client/           # Client entities
│   └── client.py
├── repositories/     # Data access layer
├── services/         # Business logic layer
└── utils/            # Utility modules
```

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/yourusername/atlas-shared-app.git
cd atlas-shared-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### Running tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
