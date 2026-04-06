from fastapi import FastAPI, HTTPException, Query, Path
import json

app = FastAPI()


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


@app.delete("/remove/patient/{patient_id}")
def remove_patient_by_id(patient_id: int):
    patients = load_data();

    for i, patient in enumerate(patients):
        if patient["id"] == patient_id:
            remove_patient = patients.pop(i)
            save_data(patients)

            return {"status": 200, "data": remove_patient, "message": "Patient removed successfully"}
        
    raise HTTPException(status_code=404, detail="No record found")