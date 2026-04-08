from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, EmailStr, Field
import json
from enum import Enum
from helpers.helpers import normalize_phone

app = FastAPI()

class GenderValid (str, Enum):
    male = "male"
    female = "female"
    others = "others"


class Address(BaseModel):
    state: str
    city: str
    pincode: int = Field(ge=100000, le=999999)



class Patient(BaseModel):
    name: str
    age: int = Field(gt=0, lt=120)
    gender: GenderValid
    phone: str = Field(min_length=10, description="Mobile number should have 10 characters", examples=["+91-xxxxxxxxxx"])
    email: EmailStr
    address: Address
    disease: str
    doctor_assigned: str
    admission_date: str
    is_discharged: bool

def load_data():
    with open("./patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("./patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def read_root():
    patients = load_data();

    if not patients:
        raise HTTPException(status_code= 400, detail="No patient registered yet")
    
    return {"status": 200, "data" : patients }

@app.get("/patient/{patient_id}")
def get_patient_by_id(patient_id: int = Path(..., description="your patient id")):
    patients = load_data();

    for patient in patients:
        if patient["id"] == patient_id:
            return {"status": 200, "data": patient}
        
    raise HTTPException(status_code=404, detail="No record found with this id")


@app.get('/patient-by-name')
def get_patient_by_name(name: str = Query(..., description= "Patient name")):
    patients = load_data();
    filter_data = [];

    for patient in patients:
        if name.lower() in patient["name"].lower():
            filter_data.append(patient);

    if not filter_data:
        raise HTTPException(status_code=404, detail="No name found");

    return {"status": 200, "data": filter_data}

@app.post("/create")
def create_patient(data: Patient):
    patients = load_data()
    dumped_data = data.model_dump()
    for patient in patients:
        if normalize_phone(patient["phone"]) == normalize_phone(dumped_data["phone"]) or patient["email"] == dumped_data["email"]:
            print("came")
            raise HTTPException(status_code=400, detail="User already found with this phone or email")
    
    dumped_data["id"] = len(patients) + 1
    patients.append(dumped_data)
    save_data(patients)
    return {"status":201, "message": "Patient created successfullt", "data": data}

# @app.put("/update/{patient_id}")
# def update_patient (patient_id: int, data : Patient):
#     patients = load_data()
#     updated_patient = data.model_dump()
#     for i,patient in enumerate(patients):
#         if patient["id"] == patient_id:
#             updated_patient["id"] = patient_id
#             patients[i] = updated_patient
#             save_data(patients)
#             return {"status": 200, "message": "Patient updated successfully", "data": data}
#     raise HTTPException(status_code=404, detail="Patient not found")

@app.put("/update/{patient_id}")
def update_patient(patient_id: int, data: Patient):
    patients = load_data()
    updated_patient = data.model_dump()

    for i, patient in enumerate(patients):
        if patient["id"] == patient_id:
            updated_patient["id"] = patient_id

            # ✅ correct assignment
            patients[i] = updated_patient

            save_data(patients)

            return {
                "status": 200,
                "message": "Patient updated successfully",
                "data": updated_patient
            }

    raise HTTPException(status_code=404, detail="Patient not found")


@app.delete("/remove/patient/{patient_id}")
def remove_patient_by_id(patient_id: int):
    patients = load_data();

    for i, patient in enumerate(patients):
        if patient["id"] == patient_id:
            remove_patient = patients.pop(i)
            save_data(patients)

            return {"status": 200, "data": remove_patient, "message": "Patient removed successfully"}
        
    raise HTTPException(status_code=404, detail="No record found")