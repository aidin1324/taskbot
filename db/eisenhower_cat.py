from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class EisenhowerCategory(Base):
    __tablename__ = "eisenhower_categories"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    
    tasks = relationship("Task", back_populates="eisenhower_category")
    
    def __repr__(self):
        return f"<EisenhowerCategory {self.name}>"