from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import functions
import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# E1 registers a package
@app.post("/packages")
def register_package(name=None, destination=None, weight: int=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not name or not destination or weight is None:
        raise HTTPException(status_code=422, detail="Missing field")
    package = functions.register_package(name=name, destination=destination, weight=weight)
    return {"message": "Package registered successfully", "package_id": package["package_id"]}

# E2 gets one package
@app.get("/packages/{package_id}")
def get_package_details(package_id: int, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

# E3 updates a package
@app.patch("/packages/{package_id}")
def update_package_details(package_id: int, name=None, destination=None, weight: int=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if name is None and destination is None and weight is None:
        raise HTTPException(status_code=422, detail="Nothing to update")
    functions.update_package_details(package_id=package_id, name=name, destination=destination, weight=weight)
    return {"message": "Package updated successfully"}

# E4 deletes a package
@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "Dispatched":
        raise HTTPException(status_code=400, detail="Cannot delete a package that has already been dispatched")
    return functions.delete_package(package_id=package_id)

# E5 searches packages
@app.get("/packages")
def search_package(destination=None, status=None, arrival_date=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    package_list = functions.search_package(destination=destination, status=status, arrival_date=arrival_date)
    if len(package_list) == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    return package_list

# E6 views dispatch batches
@app.get("/dispatch-batches")
def view_dispatchBatches(destination=None, vehicle_number: int=None, dispatch_status=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    batch_list = functions.view_dispatchBatches(destination=destination, vehicle_number=vehicle_number, dispatch_status=dispatch_status)
    if len(batch_list) == 0:
        raise HTTPException(status_code=404, detail="DispatchBatch not found")
    return batch_list

# E7 gets every dispatch batch
@app.get("/warehouse/summary")
def warehouse_summary(token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return functions.get_all_dispatchBatches()

# E8 creates a dispatch batch
@app.post("/dispatch-batches")
def add_dispatch(destination=None, vehicle_number: int=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not destination or vehicle_number is None:
        raise HTTPException(status_code=422, detail="Missing field")
    functions.create_dispatchBatches(destination=destination, vehicle_number=vehicle_number)
    return {"message": "Dispatch successfully"}

# verify login 
@app.post("/login")
def login(username: str, password: str):
    token = functions.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

# 
@app.post(path="/refresh")
def refresh(refresh_token = Header(None)):
    username = functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
    access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}