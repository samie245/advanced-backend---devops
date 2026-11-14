from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, create_engine, func
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from models import TokenPayload

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

ADMIN_USERNAME = "ratatouille"
ADMIN_PASSWORD = "remytherat"
ACCESS_TOKEN_EXPIRY = 15 # expires after that many mins
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 # 7 days in mins
SECRET_KEY = "rats&cats"
ALGORITHM = "HS256"

ph = PasswordHasher()

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    user_type = Column(String)
    username = Column(String)
    password = Column(String)

class packages(Base):
    __tablename__ = "packages"
    package_id = Column(Integer, primary_key=True)
    name = Column(String)
    destination = Column(String)
    weight = Column(Integer)
    arrival_date = Column(DateTime)
    status = Column(String)
    dispatchBatchID = Column(Integer, ForeignKey("DispatchBatch.id"), nullable=True)


class DispatchBatch(Base):
    __tablename__ = "DispatchBatch"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle_number = Column(Integer)
    dispatch_status = Column(String, default="Pending")
    dispatch_date = Column(DateTime)
    created_at = Column(String)


Base.metadata.create_all(engine)

def convert_dict(package):
    return {
        "package_id": package.package_id,
        "name": package.name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status,
    }

def convert_batch_dict(batch):
    return {
        "id": batch.id,
        "destination": batch.destination,
        "vehicle_number": batch.vehicle_number,
        "dispatch_status": batch.dispatch_status,
        "dispatch_date": batch.dispatch_date,
        "created_at": batch.created_at,
    }


# E1 registers a new package
def register_package(name, destination, weight):
    session = Session(engine)
    package = packages(
        name=name,
        destination=destination,
        weight=weight,
        arrival_date=datetime.now(),
        status="Registered"
    )
    session.add(package)
    session.commit()
    data = convert_dict(package)
    session.close()
    return data


# E2 gets one package based on id
def get_package_by_id(package_id):
    session = Session(engine)
    package = session.get(packages, package_id)
    if package is None:
        session.close()
        return None
    data = convert_dict(package)
    session.close()
    return data


# E3 updates the details of a package
def update_package_details(package_id, name=None, destination=None, weight=None):
    session = Session(engine)
    package = session.get(packages, package_id)
    if package is None:
        session.close()
        return None

    if name is not None:
        package.name = name
    if destination is not None:
        package.destination = destination
    if weight is not None:
        package.weight = weight

    session.commit()
    data = convert_dict(package)
    session.close()
    return data


# E4 removes a package
def delete_package(package_id):
    session = Session(engine)
    package = session.get(packages, package_id)
    if package is not None:
        session.delete(package)
        session.commit()
    session.close()
    return {"message": "Package deleted successfully"}


# E5 searches packages by destination, status or arrival date
def search_package(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    query = session.query(packages)

    if destination is not None:
        query = query.filter(packages.destination == destination)
    if status is not None:
        query = query.filter(packages.status == status)
    if arrival_date is not None:
        query = query.filter(func.date(packages.arrival_date) == arrival_date)
    result = []
    for package in query.all():
        result.append(convert_dict(package))
    session.close()
    return result


# E6 views dispatch batches by destination, vehicle number or status
def view_dispatchBatches(destination=None, vehicle_number=None, dispatch_status=None):
    session = Session(engine)
    result = []
    for batch in session.query(DispatchBatch).all():
        result.append(convert_batch_dict(batch))
    session.close()

    if destination is not None:
        by_destination = []
        for item in result:
            if item["destination"] == destination:
                by_destination.append(item)
        result = by_destination

    if vehicle_number is not None:
        by_vehicle = []
        for item in result:
            if item["vehicle_number"] == vehicle_number:
                by_vehicle.append(item)
        result = by_vehicle

    if dispatch_status is not None:
        by_status = []
        for item in result:
            if item["dispatch_status"] == dispatch_status:
                by_status.append(item)
        result = by_status

    return result


# E7 gets every dispatch batch
def get_all_dispatchBatches():
    session = Session(engine)
    result = []
    for batch in session.query(DispatchBatch).all():
        result.append(convert_batch_dict(batch))
    session.close()
    return result


# E8 creates a new dispatch batch
def create_dispatchBatches(destination, vehicle_number):
    session = Session(engine)
    batch = DispatchBatch(
        destination=destination,
        vehicle_number=vehicle_number,
        dispatch_status="Pending",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    session.add(batch)
    session.commit()
    data = convert_batch_dict(batch)
    session.close()
    return data


# verifying login 
def verify_login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        access_token = create_token(user_id=0, user_type="admin", username=username, token_type="access")
        refresh_token = create_token(user_id=0, user_type="admin", username=username, token_type="refresh")
        return {"access_token": access_token, "refresh_token": refresh_token}
    session = Session(engine)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    user_id = user.user_id
    user_type = user.user_type
    session.close()
    access_token = create_token(user_id=user_id, user_type=user_type, username=username, token_type="access")
    refresh_token = create_token(user_id=user_id, user_type=user_type, username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}

# creating jwt token
# jwt token has three parts:
# HEADER - its a json object that has an algorithm and token type (jwt)
# PAYLOAD - has all the meta data (claims)
#           and other registry data like: issuer (iss), subject or userid (sub), expiration (exp), issued (iat)
#           can make custom claims
# SIGNATURE - has a secret code that encodes header and payload
#           any tampering with a token makes it invalid bec of the signature secret code protection 
def create_token(user_id, user_type, username, token_type):
    time = ACCESS_TOKEN_EXPIRY # takes it as access token default, if its refresh, it changes
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY    
    payload = {
        "user_id": user_id,
        "user_type":user_type,
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

# verifying token
def verify_token(token, token_type="access"):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)
        data = TokenPayload.model_validate(payload)
    except:
        return False
    
    if  data.token_type == token_type:
        return data
    return False

# registering a user
def register_user(username: str, password: str, user_type: str):
    session = Session(engine)
    user_exists = session.query(User).filter_by(username=username).first()
    if user_exists is not None:
        session.close()
        return False
    
    session.add(User(username=username, password=ph.hash(password), user_type=user_type))
    session.commit()
    session.close()
    return True

# controlling authorizaton 
def authenticate_role(user_type, roles):
    if user_type in roles: 
        return True
    return False