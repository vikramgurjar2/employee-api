from fastapi import FastAPI, HTTPException
from models import Employee, EmployeeUpdate
from database import get_database
from typing import List

app = FastAPI(title="Employee API")
db = get_database()

@app.get("/")
def root():
    return {"message": "Employee API is running"}

# Create a new employee
@app.post("/employees", response_model=dict)
def create_employee(employee: Employee):
    # Check if employee_id already exists
    existing = db.find_one({"employee_id": employee.employee_id})
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Insert new employee
    employee_dict = employee.dict()
    result = db.insert_one(employee_dict)
    
    return {"message": "Employee created successfully", "id": str(result.inserted_id)}



# Get average salary by department
@app.get("/employees/avg-salary")
def get_avg_salary_by_department():
    pipeline = [
        {
            "$group": {
                "_id": "$department",
                "avg_salary": {"$avg": "$salary"}
            }
        },
        {
            "$project": {
                "department": "$_id",
                "avg_salary": {"$round": ["$avg_salary", 2]},
                "_id": 0
            }
        }
    ]
    
    result = list(db.aggregate(pipeline))
    return result

# Search employees by skill
@app.get("/employees/search")
def search_employees_by_skill(skill: str):
   
    employees = list(db.find({"skills": {"$regex": skill, "$options": "i"}}))
    
    
    for emp in employees:
        emp.pop('_id', None)
    
    return employees

# Get all employees, with optional filtering by department
@app.get("/employees")
def get_employees(department: str = None):
    if department:
        employees = list(db.find({"department": department}).sort("joining_date", -1))
    else:
        employees = list(db.find())
    
    for emp in employees:
        emp.pop('_id', None)
    
    return employees    


# Get an employee by employee_id
@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    employee = db.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.pop('_id', None)
    return employee

# Update an existing employee
@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, employee_update: EmployeeUpdate):
    update_data = employee_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = db.update_one(
        {"employee_id": employee_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {"message": "Employee updated successfully"}

# Delete an employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str):
    result = db.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {"message": "Employee deleted successfully"}

@app.get("/employees")
def get_employees(department: str = None, page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    
    if department:
        employees = list(db.find({"department": department})
                        .sort("joining_date", -1)
                        .skip(skip)
                        .limit(limit))
    else:
        employees = list(db.find().skip(skip).limit(limit))
    
    # Remove MongoDB _id from all records
    for emp in employees:
        emp.pop('_id', None)
    
    return {
        "employees": employees,
        "page": page,
        "limit": limit,
        "total": db.count_documents({"department": department} if department else {})
    }



# Bulk create multiple employees
@app.post("/employees/bulk", response_model=dict)
def create_employees_bulk(employees: List[Employee]):
    """
    Insert multiple employees at once.
    Validates each employee and checks for duplicate employee_ids.
    """
    if not employees:
        raise HTTPException(status_code=400, detail="Employee list cannot be empty")
    
    employee_ids = [emp.employee_id for emp in employees]
    if len(employee_ids) != len(set(employee_ids)):
        raise HTTPException(status_code=400, detail="Duplicate employee IDs found in request")
    
    existing_ids = list(db.find(
        {"employee_id": {"$in": employee_ids}}, 
        {"employee_id": 1, "_id": 0}
    ))
    
    if existing_ids:
        existing_employee_ids = [doc["employee_id"] for doc in existing_ids]
        raise HTTPException(
            status_code=400, 
            detail=f"Employee IDs already exist: {existing_employee_ids}"
        )
    
    # Convert Pydantic models to dictionaries
    employees_dict = [employee.dict() for employee in employees]
    
    try:
        result = db.insert_many(employees_dict)
        return {
            "message": f"Successfully created {len(employees)} employees",
            "inserted_count": len(result.inserted_ids),
            "inserted_ids": [str(id) for id in result.inserted_ids]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
