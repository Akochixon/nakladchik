from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, ForeignKey, String, Numeric, DateTime, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    client_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    inn: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)

class SalesAgent(Base):
    __tablename__ = "sales_agents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)

class Expediter(Base):
    __tablename__ = "expediters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(50), default="Case")

class TelegramUser(Base):
    __tablename__ = "telegram_users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    id_number: Mapped[Optional[str]] = mapped_column(String(100)) # JSHSHIR
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, approved, rejected
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

class Invoice(Base):
    __tablename__ = "invoices"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(100), index=True)
    date_str: Mapped[str] = mapped_column(String(50))
    
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    sales_agent_id: Mapped[int] = mapped_column(ForeignKey("sales_agents.id"))
    expediter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expediters.id"))
    submitted_by: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    
    total_qty: Mapped[float] = mapped_column(Numeric(10, 2))
    total_sum: Mapped[float] = mapped_column(Numeric(14, 2))
    photo_file_id: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    items: Mapped[List["InvoiceItem"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_invoice_search", "invoice_number", "customer_id", "date_str"),
    )

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    quantity: Mapped[float] = mapped_column(Numeric(10, 2))
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    line_total: Mapped[float] = mapped_column(Numeric(14, 2))
    
    invoice: Mapped["Invoice"] = relationship(back_populates="items")

class InvoiceDuplicate(Base):
    __tablename__ = "invoice_duplicates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    submitted_by: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    decision: Mapped[str] = mapped_column(String(20)) # confirmed_as_duplicate
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# models.py oxiriga qo'shasiz
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    action: Mapped[str] = mapped_column(String(100))  # masalan: "create_invoice", "duplicate_approved", "edit_invoice"
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)