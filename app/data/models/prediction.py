from typing import Dict, Any, List
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy import subquery
from sqlalchemy import select

from sqlalchemy.dialects.postgresql import aggregate_order_by

from app.data import db
from app.data.processing.predictive_models import latest_model_outputs


class Prediction(db.Model):
    __tablename__ = 'prediction'
    reach_id = db.Column(
        db.Integer, db.ForeignKey('reach.id'),
        primary_key=True, nullable=False)
    time = db.Column(db.DateTime, primary_key=True, nullable=False)
    probability = db.Column(db.Numeric)
    safe = db.Column(db.Boolean)

    reach = db.relationship('Reach', back_populates='predictions')

    @classmethod
    def _latest_ts_scalar_subquery(cls):
        return select(func.max(Prediction.time)).as_scalar()

    @classmethod
    def get_latest(cls, reach: int) -> 'Prediction':
        return (
            db.session
            .query(cls)
            .filter(and_(
                cls.time == cls._latest_ts_scalar_subquery(),
                cls.reach == reach))
            .first()
        )

    @classmethod
    def get_all_latest(cls) -> List['Prediction']:
        return (
            db.session
            .query(cls)
            .filter(cls.time == cls._latest_ts_scalar_subquery())
            .all()
        )


def get_latest_prediction_time() -> datetime:
    return db.session.query(func.max(Prediction.time)).scalar()
