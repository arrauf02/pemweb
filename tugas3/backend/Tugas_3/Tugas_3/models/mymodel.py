from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    DateTime,
)
from datetime import datetime
import json
from .meta import Base

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20))     # POSITIVE/NEGATIVE
    confidence = Column(Float)         # 0.0 - 1.0
    key_points = Column(Text)          # Disimpan sebagai JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'review_text': self.review_text,
            'sentiment': self.sentiment,
            'confidence': self.confidence,
            'key_points': json.loads(self.key_points) if self.key_points else [],
            'created_at': self.created_at.isoformat()
        }