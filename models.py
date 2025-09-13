from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Employee(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: int
    joining_date: str
    skills: List[str]

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[int] = None
    joining_date: Optional[str] = None
    skills: Optional[List[str]] = None