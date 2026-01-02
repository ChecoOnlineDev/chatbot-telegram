from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Integer, Enum as SqlAlchemyEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.domain.constants import TechnicalServiceStatus #importamos el enum para darlo como molde a la bd

class Base(DeclarativeBase):
    pass

class TechnicalService(Base):
    __tablename__ = "technical_services"

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    folio: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    #utilizamos nuestro enum de estados para darlo como base a la bd
    status: Mapped[TechnicalServiceStatus] = mapped_column(
        SqlAlchemyEnum(TechnicalServiceStatus), 
        nullable=False
    )
    reception_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    service_reason: Mapped[str] = mapped_column(String(500), nullable=False)

    #campos opcionles
    service_summary: Mapped[Optional[str]] = mapped_column(String(1000))
    on_hold_reason: Mapped[Optional[str]] = mapped_column(String(255))
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255))
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)