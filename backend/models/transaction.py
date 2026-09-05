from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from backend.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), default="Disbursement") # Release, Expenditure, Refund
    recipient = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    milestone_name = Column(String(255), nullable=False)
    target_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="Pending") # Pending, Completed, Delayed, In Progress
    percentage_weight = Column(Float, default=0.0)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
