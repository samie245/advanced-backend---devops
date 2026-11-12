from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

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
    result = []
    for package in session.query(packages).all():
        result.append(convert_dict(package))
    session.close()

    if destination is not None:
        by_destination = []
        for item in result:
            if item["destination"] == destination:
                by_destination.append(item)
        result = by_destination

    if status is not None:
        by_status = []
        for item in result:
            if item["status"] == status:
                by_status.append(item)
        result = by_status

    if arrival_date is not None:
        by_date = []
        for item in result:
            if str(item["arrival_date"])[:10] == arrival_date:
                by_date.append(item)
        result = by_date

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