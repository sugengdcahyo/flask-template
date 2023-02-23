from core.database import db

from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr



class Base(db.Model):
    """This Base class does nothing. It is here is case I need to expand
    implement something later. I feel like it's a good early practice.

    Attributes
    ----------
    id : int
        The basic primary key id number of any class.

    Notes
    -----
    The __tablename__ is automatically set to the class name lower-cased.
    There's no need to mess around with underscores, that just confuses the
    issue and makes programmatically referencing the table more difficult.
    """
    __abstract__ = True
    _id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=int(datetime.utcnow().timestamp()))
    updated_at = db.Column(db.Integer, default=int(datetime.utcnow().timestamp()))

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


    def save(self):
        if self._id:
            db.session.query(self.__class__) \
                .get(self._id)
            db.session.add(self)
            db.session.commit()
        else:
            db.session.add(self)
            db.session.commit()

    
    def delete(self):
        pass

    
    def bulk_save(self, instances):
        db.session.bulk_save_objects(instances)
        db.session.commit()