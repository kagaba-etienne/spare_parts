from sqlalchemy import Column, Integer, String, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship
from app.db import Base

accessory_fitment = Table('accessory_fitment', Base.metadata,
                          Column('fitment_id', Integer, ForeignKey('trims_engines_and_cars.id', ondelete='CASCADE')),
                          Column('accessory_id', Integer, ForeignKey('accessories.id', ondelete='CASCADE'))
                          )

part_sub_cat_fitment = Table('part_sub_cat_fitment', Base.metadata,
                             Column('fitment_id', Integer, ForeignKey('trims_engines_and_cars.id', ondelete='CASCADE')),
                             Column('sub_cat_id', Integer, ForeignKey('parts_subcategories.id', ondelete='CASCADE')))

acc_sub_cat_fitment = Table('acc_sub_cat_fitment', Base.metadata,
                            Column('fitment_id', Integer, ForeignKey('trims_engines_and_cars.id', ondelete='CASCADE')),
                            Column('sub_cat_id', Integer, ForeignKey('acc_subcategories.id', ondelete='CASCADE')))

car_fitment = Table('car_fitments', Base.metadata,
                    Column('fitment_id', Integer, ForeignKey('trims_engines_and_cars.id', ondelete='CASCADE')),
                    Column('car_id', Integer, ForeignKey('cars.id', ondelete='CASCADE')))

part_fitment = Table('part_fitment', Base.metadata,
                     Column('fitment_id', Integer, ForeignKey('trims_engines_and_cars.id', ondelete='CASCADE')),
                     Column('part_id', Integer, ForeignKey('parts.id', ondelete='CASCADE')))


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    trims = relationship('Trim', secondary='trims_cars', back_populates='cars')
    fitments = relationship('TrimEngineAndCar', secondary='car_fitments', back_populates='cars')


class Trim(Base):
    __tablename__ = 'trims'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trim = Column(String)
    cars = relationship('Car', secondary='trims_cars', back_populates='trims')


class TrimCar(Base):
    __tablename__ = 'trims_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id', ondelete='CASCADE'))
    trim_id = Column(Integer, ForeignKey('trims.id', ondelete='CASCADE'))
    engines = relationship('Engine', secondary='trims_engines_and_cars', back_populates='trims_and_cars')


class Engine(Base):
    __tablename__ = 'engines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    engine = Column(String)
    trims_and_cars = relationship('TrimCar', secondary='trims_engines_and_cars', back_populates='engines')


class Part(Base):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_num = Column(String)
    name = Column(String)
    price = Column(String)
    other_names = Column(ARRAY(String))
    images = Column(ARRAY(String))
    description = Column(String)
    replaces = Column(ARRAY(String))
    condition = Column(String)
    brands = Column(ARRAY(String))
    positions = Column(ARRAY(String))
    subcategory_id = Column(Integer, ForeignKey('parts_subcategories.id', ondelete='CASCADE'))
    subcategory = relationship('Subcategory', back_populates='parts')
    fits = relationship('TrimEngineAndCar', secondary='part_fitment', back_populates='parts')


class TrimEngineAndCar(Base):
    __tablename__ = 'trims_engines_and_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    engine_id = Column(Integer, ForeignKey('engines.id', ondelete='CASCADE'))
    trim_car_id = Column(Integer, ForeignKey('trims_cars.id', ondelete='CASCADE'))
    parts = relationship('Part', secondary='part_fitment', back_populates='fits')
    accessories = relationship('Accessory', secondary='accessory_fitment', back_populates='fits')
    parts_subcategories = relationship('Subcategory', secondary=part_sub_cat_fitment, back_populates='fits')
    acc_subcategories = relationship('ASubcategory', secondary=acc_sub_cat_fitment, back_populates='fits')
    cars = relationship('Car', secondary='car_fitments', back_populates='fitments')


class Accessory(Base):
    __tablename__ = 'accessories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_num = Column(String)
    name = Column(String)
    price = Column(String)
    other_names = Column(ARRAY(String))
    images = Column(ARRAY(String))
    description = Column(String)
    replaces = Column(ARRAY(String))
    condition = Column(String)
    brands = Column(ARRAY(String))
    positions = Column(ARRAY(String))
    subcategory_id = Column(Integer, ForeignKey('acc_subcategories.id', ondelete='CASCADE'))
    subcategory = relationship('ASubcategory', back_populates='accessories')
    fits = relationship('TrimEngineAndCar', secondary='accessory_fitment', back_populates='accessories')
