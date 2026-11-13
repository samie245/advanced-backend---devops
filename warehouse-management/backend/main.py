from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import functions
from models import PackageCreate, DispatchBatchCreate, LoginRequest, PackageUpdate, PackageSearch, DispatchBatchSearch, PackageOut, TokenPair, SignupRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# E1 registers a package
@app.post("/packages")
def register_package(package: PackageCreate, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    new_package = functions.register_package(name=package.name, destination=package.destination, weight=package.weight)
    return {"message": "Package registered successfully", "package_id": new_package["package_id"]}

# E2 gets one package
@app.get("/packages/{package_id}", response_model=PackageOut)
def get_package_details(package_id: int, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin", "delivery_partner", "customer"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

# E3 updates a package
@app.patch("/packages/{package_id}")
def update_package_details(package_id: int, update: PackageUpdate, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    functions.update_package_details(package_id=package_id, name=update.name, destination=update.destination, weight=update.weight)
    return {"message": "Package updated successfully"}

# E4 deletes a package
@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    package = functions.get_package_by_id(package_id=package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "Dispatched":
        raise HTTPException(status_code=400, detail="Cannot delete a package that has already been dispatched")
    return functions.delete_package(package_id=package_id)

# E5 searches packages
@app.get("/packages", response_model=list[PackageOut])
def search_package(destination=None, status=None, arrival_date=None, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin", "delivery_partner", "customer"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    try:
        filters = PackageSearch(destination=destination, status=status, arrival_date=arrival_date)
    except:
        raise HTTPException(status_code=422, detail="Bad input")
    package_list = functions.search_package(destination=filters.destination, status=filters.status, arrival_date=filters.arrival_date)
    if len(package_list) == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    return package_list

# E6 views dispatch batches
@app.get("/dispatch-batches")
def view_dispatchBatches(destination=None, vehicle_number: int=None, dispatch_status=None, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin", "delivery_partner"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    try:
        filters = DispatchBatchSearch(destination=destination, vehicle_number=vehicle_number, dispatch_status=dispatch_status)
    except:
        raise HTTPException(status_code=422, detail="Bad input")
    batch_list = functions.view_dispatchBatches(destination=filters.destination, vehicle_number=filters.vehicle_number, dispatch_status=filters.dispatch_status)
    if len(batch_list) == 0:
        raise HTTPException(status_code=404, detail="DispatchBatch not found")
    return batch_list

# E7 gets every dispatch batch
@app.get("/warehouse/summary")
def warehouse_summary(token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin", "delivery_partner"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    return functions.get_all_dispatchBatches()

# E8 creates a dispatch batch
@app.post("/dispatch-batches")
def add_dispatch(batch: DispatchBatchCreate, token = Header(None)):
    user = functions.verify_token(token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not functions.authenticate_role(user_type=user.user_type, roles=["admin"]):
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    functions.create_dispatchBatches(destination=batch.destination, vehicle_number=batch.vehicle_number)
    return {"message": "Dispatch successfully"}

# verify login
@app.post("/login", response_model=TokenPair)
def login(creds: LoginRequest):
    token = functions.verify_login(username=creds.username, password=creds.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

# refresh token
@app.post(path="/refresh")
def refresh(refresh_token = Header(None)):
    user = functions.verify_token(token=refresh_token, token_type="refresh")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
    access_token = functions.create_token(user_id=user.user_id, user_type=user.user_type, username=user.username, token_type="access")
    return {"access_token": access_token}


# registers a user, admin is not allowed here because the admin is hard coded
@app.post(path="/signup")
def register_user(creds: SignupRequest):
    if functions.register_user(username=creds.username, password=creds.password, user_type=creds.user_type):
        return {"message": "User registered sucessfully"}
    raise HTTPException(status_code=400, detail="User already exists")