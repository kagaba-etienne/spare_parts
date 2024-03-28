from fastapi import APIRouter, Query
from app.db import get_db
from app.db.models import Car, TrimCar
from app.api.endpoints import Res
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter()


def get_models(db: Session) -> Res:
    cars = db.query(Car.model).filter_by(make="Toyota").distinct().order_by(Car.model.asc()).all()
    car_models = [car[0] for car in cars]

    response = Res(status=200, message="Models retrieved successfully!", data={
        "make": "Toyota",
        "models": car_models})
    return response


def get_years(db: Session, model: str) -> Res:
    cars = db.query(Car.year).filter_by(model=model, make="Toyota").distinct().order_by(Car.year.desc()).all()
    car_years = [car[0] for car in cars]

    response = Res(status=200, message="Years retrieved successfully!", data={
        "make": "Toyota",
        "model": model,
        "years": car_years})
    return response


def get_trims_and_engines(db: Session, model: str, year: str) -> Res:
    car = db.query(Car).filter_by(model=model, year=year, make="Toyota").first()
    trims_and_engines = []

    if car:
        trims = car.trims
        for trim in trims:
            trim_car = db.query(TrimCar).filter_by(car_id=car.id, trim_id=trim.id).first()
            if trim_car:
                engines = trim_car.engines

                for engine in engines:
                    trims_and_engines.append(trim.trim + " " + engine.engine)

    response = Res(status=200, message="Trims and Engines retrieved successfully!", data={
        "make": "Toyota",
        "model": model,
        "year": year,
        "trims_and_engines": trims_and_engines})
    return response


@router.get("/" ,response_model=Res)
def get_cars(db: Session = Depends(get_db), model: str = Query(None, description="Model name"),
             year: str = Query(None, description="Model year")) -> Res:
    if model and year:
        return get_trims_and_engines(db, model, year)
    elif model and not year:
        return get_years(db, model)
    else:
        return get_models(db)
