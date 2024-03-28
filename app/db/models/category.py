from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from .car import part_sub_cat_fitment, acc_sub_cat_fitment


class Category(Base):
    __tablename__ = 'parts_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    subcategories = relationship('Subcategory', back_populates='category', cascade='all')


class Subcategory(Base):
    __tablename__ = 'parts_subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey('parts_categories.id', ondelete='CASCADE'))
    category = relationship('Category', back_populates='subcategories', cascade='all')
    parts = relationship('Part', back_populates='subcategory', cascade='all')
    fits = relationship('TrimEngineAndCar', secondary=part_sub_cat_fitment, back_populates='parts_subcategories')


class ACategory(Base):
    __tablename__ = 'acc_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    subcategories = relationship('ASubcategory', back_populates='category', cascade='all')


class ASubcategory(Base):
    __tablename__ = 'acc_subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey('acc_categories.id', ondelete='CASCADE'))
    category = relationship('ACategory', back_populates='subcategories', cascade='all')
    accessories = relationship('Accessory', back_populates='subcategory', cascade='all')
    fits = relationship('TrimEngineAndCar', secondary=acc_sub_cat_fitment, back_populates='acc_subcategories')
