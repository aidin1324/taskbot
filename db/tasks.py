from .db import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    notify_at = Column(DateTime, index=True)
    start_date = Column(DateTime, index=True)
    due_date = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)
    estimated_time = Column(Integer, index=True)
    eisenhower_cat_id = Column(Integer, ForeignKey("eisenhower_categories.id"), index=True)
    
    eisenhower_category = relationship("EisenhowerCategory", back_populates="tasks")
    
    
    def __repr__(self):
        return f"<Task {self.title}>"
    
    
    
    
    