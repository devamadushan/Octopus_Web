'''
pip install Flask-SQLAlchemy

'''
##############################################################################################


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer,String,DATE, ForeignKey
from sqlalchemy.orm import relationship
from flask import Flask
from conn import Base, DB_URL



##############################################################################################

db = SQLAlchemy()


class Experience(Base):
    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True)
    date_debut = Column(DATE)
    date_fin = Column(DATE)
    nom = Column(String(255), nullable=False)
    etat_experience = Column(String(255))


    # Relation ONE TO MANY
   
    cellules = relationship('Cellule', backref='experience') 
   
    

Base.metadata.create_all(DB_URL)