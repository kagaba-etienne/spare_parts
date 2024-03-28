from fastapi import APIRouter, Query, Path
from app.db import get_db
from app.db.models import Accessory, Part, ASubcategory, Subcategory, Car, TrimCar, Engine, TrimEngineAndCar, Trim
from app.api.endpoints import Res, Scope
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from fastapi import Depends
from app.db import Base

router = APIRouter()


def get_query(scope: Scope = Scope.parts):
    if scope == Scope.parts:
        model = 'parts'
    else:
        model = 'accessories'
    query = text(f'''
            SELECT *
            FROM {model} AS p
            WHERE p.id IN (
                SELECT DISTINCT(p_f.part_id)
                FROM part_fitment AS p_f
                WHERE p_f.fitment_id IN (
                    SELECT DISTINCT(tec.id)
                    FROM trims_engines_and_cars AS tec
                    WHERE tec.id IN (
                        SELECT DISTINCT(c_f.fitment_id)
                        FROM car_fitments AS c_f
                        WHERE c_f.car_id IN (
                            SELECT c.id
                            FROM cars AS c
                            WHERE (:model IS NULL OR c.model LIKE '%' || :model || '%') 
                            AND (:make IS NULL OR c.make LIKE '%' || :make || '%') 
                            AND (c.year = COALESCE(:year, c.year))
                        )
                    )
                )
            ) AND
            (
                (:search_term IS NULL) OR
                (
                    SIMILARITY(LOWER(p.name), :search_term) > 0.25 OR
                    SIMILARITY(LOWER(p.part_num), :search_term) > 0.25 OR
                    SIMILARITY(LOWER(p.description), :search_term) > 0.25
                )
            )
            ORDER BY
            (
                CASE WHEN :search_term IS NULL THEN 0 ELSE
                (
                    SIMILARITY(LOWER(p.name), :search_term) +
                    SIMILARITY(LOWER(p.part_num), :search_term) +
                    SIMILARITY(LOWER(p.description), :search_term)
                ) END
            ) DESC;
            ''')
    return query


def make_part(part: Base):
    new_part = {
        "id": part.id,
        "part_num": part.part_num,
        "name": part.name,
        "price": part.price,
        "other_names": part.other_names,
        "images": part.images,
        "description": part.description,
        "replaces": part.replaces,
        "condition": part.condition,
        "brands": part.brands,
        "positions": part.positions,
        "sub_category": part.subcategory.name,
    }

    return new_part


def make_part_filter(db: Session, part: Base, scope: Scope = Scope.parts):
    if scope == Scope.parts:
        sub_cat = db.query(Subcategory).filter_by(id=part.subcategory_id).first()
    else:
        sub_cat = db.query(ASubcategory).filter_by(id=part.subcategory_id).first()
    new_part = {
        "id": part.id,
        "part_num": part.part_num,
        "name": part.name,
        "price": part.price,
        "other_names": part.other_names,
        "images": part.images,
        "description": part.description,
        "replaces": part.replaces,
        "condition": part.condition,
        "brands": part.brands,
        "positions": part.positions,
        "sub_category": sub_cat.name
    }

    return new_part


def get_similar(db: Session, model: Base = None, search_term: str = None):
    return db.query(model).filter_by().filter(
        or_(func.similarity(func.lower(model.name), search_term.lower()) > 0.25,
            func.similarity(func.lower(model.part_num), search_term.lower()) > 0.25,
            func.similarity(func.lower(model.description), search_term.lower()) > 0.25)
    ).order_by((func.similarity(func.lower(model.name), search_term.lower()) +
                func.similarity(func.lower(model.part_num), search_term.lower()) +
                func.similarity(func.lower(model.description), search_term.lower())).desc()).all()


def get_parts_by_config(db: Session, model: str, make: str, year: str, trim: str, engine: str, sub_cat: Base = None,
                        scope: Scope = Scope.parts, search: str = None) -> Res:
    car = db.query(Car).filter_by(model=model, make=make, year=year).first()
    trim = db.query(Trim).filter_by(trim=trim).first()
    engine = db.query(Engine).filter_by(engine=engine).first()
    parts_list = []
    if car and trim and engine:
        trim_car = db.query(TrimCar).filter_by(car_id=car.id, trim_id=trim.id).first()
        if trim_car:
            trim_engine_car = db.query(TrimEngineAndCar).filter_by(engine_id=engine.id, trim_car_id=trim_car.id).first()
            if trim_engine_car:
                if search and scope == Scope.parts:
                    parts = get_similar(db, Part, search)
                elif search and scope == Scope.accessories:
                    parts = get_similar(db, Accessory, search)
                elif scope == Scope.parts:
                    parts = trim_engine_car.parts
                else:
                    parts = trim_engine_car.accessories
                for part in parts:
                    if sub_cat:
                        if part.subcategory.name != sub_cat.name:
                            continue
                    parts_list.append(make_part(part))
    if scope == Scope.parts:
        res = Res(status=200, message="Parts retrieved successfully!", data={
            "length": len(parts_list),
            "parts": parts_list
        })
    else:
        res = Res(status=200, message="Parts retrieved successfully!", data={
            "length": len(parts_list),
            "categories": parts_list
        })

    return res


def get_parts_by_filter(db: Session, model: str = None, make: str = "Toyota", year: str = None,
                        scope: Scope = Scope.parts, search: str = None):
    results = db.execute(get_query(scope), {
        'search_term': search,
        "model": model,
        "year": year,
        "make": make
    })
    new_results = []
    for result in results:
        new_results.append(make_part_filter(db, result, scope))
    res = Res(status=200, message="Parts retrieved successfully", data={
        "length": len(new_results),
        'parts': new_results
    })
    return res


@router.get("/", response_model=Res)
def get_parts(db: Session = Depends(get_db),
              model: str = Query(None, description="Model name"),
              make: str = Query('Toyota', description="Car make name"),
              year: str = Query(None, description="Production year"),
              trim: str = Query(None, description="Car Trim Level"),
              engine: str = Query(None, description="Engine type"),
              sub_cat: str = Query(None, description="Subcategory name"),
              search: str = Query(None, description="Search text"),
              scope: Scope = Query(Scope.parts, description="Scope of categories")):
    if (isinstance(model, str) and isinstance(make, str) and isinstance(year, str)
            and isinstance(trim, str) and isinstance(engine, str)):
        if scope == Scope.parts:
            sub_category = db.query(Subcategory).filter_by(name=sub_cat).first()
            return get_parts_by_config(db, model, make, year, trim, engine, sub_category, scope, search)
        else:
            sub_category = db.query(ASubcategory).filter_by(name=sub_cat).first()
            return get_parts_by_config(db, model, make, year, trim, engine, sub_category, scope, search)
    else:
        return get_parts_by_filter(db, model, make, year, scope, search)


@router.get("/{id_}", response_model=Res)
def get_part(db: Session = Depends(get_db),
             id_: int = Path(..., description="Part/Accessory Id"),
             scope: Scope = Query(Scope.parts, description="Scope of part")) -> Res:
    if scope == Scope.parts:
        part = db.query(Part).filter_by(id=id_).first()
    else:
        part = db.query(Accessory).filter_by(id=id_).first()

    fitment_list = {}
    new_part = make_part(part)
    fits = part.fits
    for fit in fits:
        engine = db.query(Engine).filter_by(id=fit.engine_id).first()
        trim_car = db.query(TrimCar).filter_by(id=fit.trim_car_id).first()

        car = db.query(Car).filter_by(id=trim_car.car_id).first()
        trim = db.query(Trim).filter_by(id=trim_car.trim_id).first()

        car = [car.year, car.make, car.model]
        car = tuple(car)
        if car in fitment_list.keys():
            fitment_list[car]["trims"].add(trim.trim)
            fitment_list[car]["engines"].add(engine.engine)
        else:
            fitment_list[car] = {
                "trims": {trim.trim},
                "engines": {engine.engine}
            }
    new_fitments = []
    for fit in fitment_list.keys():
        new_fitments.append({
            "year": fit[0],
            "make": fit[1],
            "model": fit[2],
            "trims": list(fitment_list[fit]["trims"]),
            "engines": list(fitment_list[fit]["engines"])
        })
    res = Res(status=200, message="Part retrieved successfully!", data={
        "part": new_part,
        "fitments": new_fitments
    })

    return res
