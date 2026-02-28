# HikCentral OpenAPI Client

A Python async client library for interacting with the HikCentral OpenAPI.

This package provides typed models and helper methods for common resource and ACS workflows, including:

- Version discovery and client initialization
- Organization management
- Access level retrieval and assignment
- Person lifecycle management (including face updates)

## Installation

Install with `uv`:

```bash
uv pip install hikcentral-openapi
```

Or with `pip`:

```bash
pip install hikcentral-openapi
```

## Quick Start

### Initialize the Client

```python
from hikcentral_openapi import Client

client = Client(
    user_key="your-user-key",
    user_secret="your-user-secret",
    host="localhost",
    port=443,
)

await client.initialize()
print(client.version)
```

### Use a Custom `httpx.AsyncClient`

```python
import httpx
from hikcentral_openapi import Client

httpx_client = httpx.AsyncClient(verify=False)
client = Client(
    user_key="your-user-key",
    user_secret="your-user-secret",
    httpx_client=httpx_client,
)
```

## Usage Examples

### Organizations

```python
# Get all organizations
orgs = await client.get_organization()

# Filter organizations by name
filtered_orgs = await client.get_organization(name="Head Office")

# Get the root organization
root = await client.get_root_organization()

# Add organization under root automatically
new_org = await client.add_organization(name="Engineering")

# Add organization under explicit parent
child_org = await client.add_organization(
    name="R&D",
    parent_id=new_org.org_id,
)

# Update organization
child_org.org_name = "Research and Development"
await client.update_organization(child_org)

# Delete organization
await client.delete_organization(org_id=child_org.org_id)
```

### Access Levels

```python
# Retrieve all access levels
access_levels = await client.get_access_level()

# Assign one access level to one or more persons
level = access_levels[0]
await client.assign_access_level(
    access_level=level,
    person_id=["person-id-1", "person-id-2"],
)

# Remove assignment
await client.unassign_access_level(
    access_level=level,
    person_id=["person-id-2"],
)
```

### Persons

```python
from datetime import datetime, timezone
from hikcentral_openapi.models import Card, Person

# Get person by ID
person = await client.get_person(person_id="person-id-1")

# Search persons by name
persons_by_name = await client.get_person(name="John")

# Search persons by card number
persons_by_card = await client.get_person(card_no="1234567890")

# Add new person
new_person = Person(
    person_code="EMP-0001",
    person_name="John Doe",
    org_index_code="org-index-code",
    phone_no="+1-555-1000",
    email="john.doe@example.com",
    cards=[Card(card_no="1234567890")],
    begin_time=datetime.now(timezone.utc),
)
new_person_id = await client.add_person(new_person)

# Update person
new_person.person_id = new_person_id
new_person.person_name = "John A. Doe"
await client.update_person(new_person)

# Update person face (face_data is expected as base64 string)
await client.update_person_face(
    person_id=new_person_id,
    face_data="base64-encoded-face-image",
)

# Delete person
await client.delete_person(person_id=new_person_id)
```

## Data Models

Main models are available in `hikcentral_openapi.models`:

- `Organization`
- `AccessLevel`
- `Person`
- `Card`
- `Face`
- `CustomField`

## Error Handling

The library raises typed exceptions from `hikcentral_openapi.exceptions`:

- `HikApiError`: Base exception
- `ConnectError`: Transport-level connection errors
- `UnauthorizedError`: Authentication/authorization failures
- `RequestError`: API request or validation errors returned by the server

```python
from hikcentral_openapi import Client, HikApiError

try:
    await client.initialize()
except HikApiError as err:
    print(f"HikCentral API error: {err}")
```

## API Reference

- Client implementation: `src/hikcentral_openapi/client.py`
- Models: `src/hikcentral_openapi/models.py`
- Exceptions: `src/hikcentral_openapi/exceptions.py`
