# Employee API

Simple REST API for managing employee records using FastAPI and MongoDB.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Make sure MongoDB is running locally, then start the server:
```bash
python -m uvicorn main:app --reload
```

API will be available at http://localhost:8000

## Endpoints

**Basic CRUD:**
- `POST /employees` - Create employee  
- `GET /employees/{employee_id}` - Get employee by ID
- `PUT /employees/{employee_id}` - Update employee
- `DELETE /employees/{employee_id}` - Delete employee

**Queries:**
- `GET /employees?department=Engineering` - Filter by department
- `GET /employees/search?skill=Python` - Search by skill  
- `GET /employees/avg-salary` - Average salary by department



## Employee Structure
```json
{
  "employee_id": "E123",
  "name": "John Doe",
  "department": "Engineering", 
  "salary": 75000,
  "joining_date": "2023-01-15",
  "skills": ["Python", "MongoDB", "APIs"]
}
```

Uses MongoDB database `assessment_db` with collection `employees`.
