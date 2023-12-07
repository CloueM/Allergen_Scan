from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from base import Base
import datetime

class IngredientSuggestion(Base):
    """
    Ingredient Suggestions
    
    - id
    - user_id
    - user_name
    - barcode
    - product_name
    - suggested_ingredient
    - suggestion_details
    - date_created
    - trace_id
    
    """
    __tablename__ = "ingredient_suggestion"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(250), nullable=False)
    barcode = Column(BigInteger, nullable=False)
    product_name = Column(String(100), nullable=False)
    suggested_ingredient = Column(String(100), nullable=False)
    suggestion_details = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=True)

    def __init__(self, user_id, user_name, barcode, product_name, suggested_ingredient, suggestion_details, trace_id):
        self.user_id = user_id
        self.user_name = user_name
        self.barcode = barcode
        self.product_name = product_name
        self.suggested_ingredient = suggested_ingredient
        self.suggestion_details = suggestion_details
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['user_id'] = self.user_id
        data['user_name'] = self.user_name
        data['barcode'] = self.barcode
        data['product_name'] = self.product_name
        data['suggested_ingredient'] = self.suggested_ingredient
        data['suggestion_details'] = self.suggestion_details
        data['date_created'] = self.date_created
        data['trace_id'] = self.trace_id

        return data
