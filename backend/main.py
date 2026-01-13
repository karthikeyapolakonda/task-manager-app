from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini ERP API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- AUTH ----------
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    return {"message": "User registered"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()
    if not user or not auth.verify_password(password, user.password):
        return {"error": "Invalid credentials"}
    return {"message": "Login success", "role": user.role}

# ---------- EMPLOYEE ----------
@app.post("/employees")
def add_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    employee = models.Employee(**emp.dict())
    db.add(employee)
    db.commit()
    return {"message": "Employee added"}

@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

# ---------- ATTENDANCE ----------
@app.post("/attendance")
def mark_attendance(att: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    record = models.Attendance(**att.dict())
    db.add(record)
    db.commit()
    return {"message": "Attendance marked"}