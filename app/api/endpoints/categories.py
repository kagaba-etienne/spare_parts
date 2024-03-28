from fastapi import APIRouter, Query
from app.db import get_db
from app.db.models import Category, ACategory, Car, TrimCar, Engine, TrimEngineAndCar, Trim
from app.api.endpoints import Res, Scope
from sqlalchemy.orm import Session
from fastapi import Depends
from collections import defaultdict

router = APIRouter()


def get_categories(db: Session, model, scope: Scope = Scope.parts) -> Res:
    categories = db.query(model).all()

    cat_list = []
    for cat in categories:
        sub_categories = cat.subcategories
        sub_cat_list = []
        for sub_cat in sub_categories:
            sub_cat_list.append(sub_cat.name)
        cat_list.append({
            "category": cat.name,
            "sub_categories": sub_cat_list
        })

    response = Res(status=200, message="Categories retrieved successfully", data={
        "scope": scope,
        "categories": cat_list})
    return response


def get_cat_by_config(db: Session, model: str, make: str, year: str, trim: str, engine: str) -> Res:
    car = db.query(Car).filter_by(model=model, make=make, year=year).first()
    acc_sub_categories_list = defaultdict(set)
    parts_sub_categories_list = defaultdict(set)
    if car:
        _trim = db.query(Trim).filter_by(trim=trim).first()
        if _trim:
            trim_car = db.query(TrimCar).filter_by(trim_id=_trim.id, car_id=car.id).first()
            if trim_car:
                _engine = db.query(Engine).filter_by(engine=engine).first()
                if _engine:
                    trim_engine_car = (db.query(TrimEngineAndCar)
                                       .filter_by(engine_id=_engine.id, trim_car_id=trim_car.id).first())
                    if trim_engine_car:
                        acc_sub_categories = trim_engine_car.acc_subcategories
                        parts_sub_categories = trim_engine_car.parts_subcategories

                        for acc_sub in acc_sub_categories:
                            acc_sub_categories_list[acc_sub.category.name].add(acc_sub.name)
                        for part_sub in parts_sub_categories:
                            parts_sub_categories_list[part_sub.category.name].add(part_sub.name)
    new_acc_sub_categories_list = []
    new_parts_sub_categories_list = []
    for acc_sub in acc_sub_categories_list:
        new_acc_sub_categories_list.append({
            "category": acc_sub,
            "sub_categories": list(acc_sub_categories_list[acc_sub])
        })
    for part_sub in parts_sub_categories_list:
        new_parts_sub_categories_list.append({
            "category": part_sub,
            "sub_categories": list(parts_sub_categories_list[part_sub])
        })
    response = Res(status=200, message="Categories Retrieved Successfully", data={
        "parts_categories": new_parts_sub_categories_list,
        "acc_categories": new_acc_sub_categories_list
    })
    return response


@router.get("/", response_model=Res)
def get_cats_and_subs(db: Session = Depends(get_db),
                      model: str = Query(None, description="Model name"),
                      make: str = Query('Toyota', description="Car make name"),
                      year: str = Query(None, description="Production year"),
                      trim: str = Query(None, description="Car Trim Level"),
                      engine: str = Query(None, description="Engine type"),
                      scope: Scope = Query(Scope.parts, description="scope of categories")) -> Res:
    if (isinstance(model, str) and isinstance(make, str) and isinstance(year, str)
            and isinstance(trim, str) and isinstance(engine, str)):
        return get_cat_by_config(db, model, make, year, trim, engine)
    elif scope == Scope.parts:
        return get_categories(db, Category, scope)
    else:
        return get_categories(db, ACategory, scope)
