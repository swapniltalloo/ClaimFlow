import os
from datetime import datetime, timezone
from typing import AsyncGenerator
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, JSON, Text, ForeignKey, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import relationship, sessionmaker
from app.core.config import settings

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClaimRecord(Base):
    __tablename__ = "claims"

    claim_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), index=True, nullable=False)
    hospital_id = Column(String(64), index=True, nullable=False)
    policy_id = Column(String(64), index=True, nullable=False)
    admission_time = Column(DateTime, nullable=False)
    discharge_time = Column(DateTime, nullable=False)
    total_claimed_amount = Column(Float, nullable=False)
    total_approved_amount = Column(Float, default=0.0)
    status = Column(String(32), default="INGESTED")
    risk_score = Column(Float, default=0.0)
    risk_reasons = Column(JSON, default=list)
    clinical_facts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    settled_at = Column(DateTime, nullable=True)
    is_fraud = Column(Boolean, default=False)
    fraud_pattern = Column(String(64), nullable=True)

    line_items = relationship("LineItemRecord", back_populates="claim", cascade="all, delete-orphan")
    decision = relationship("DecisionRecord", back_populates="claim", uselist=False)


class LineItemRecord(Base):
    __tablename__ = "claim_line_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(64), ForeignKey("claims.claim_id"), index=True)
    line_number = Column(Integer, nullable=False)
    service_date = Column(DateTime, nullable=False)
    item_type = Column(String(32), nullable=False)
    code = Column(String(32), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    verdict = Column(String(32), default="PENDING")
    verdict_reasons = Column(JSON, default=list)
    clause_citations = Column(JSON, default=list)
    approved_amount = Column(Float, nullable=True)
    is_fraudulent = Column(Boolean, default=False)
    injected_fraud_pattern = Column(String(64), nullable=True)

    claim = relationship("ClaimRecord", back_populates="line_items")


class DecisionRecord(Base):
    __tablename__ = "decisions"

    decision_id = Column(String(64), primary_key=True, index=True)
    claim_id = Column(String(64), ForeignKey("claims.claim_id"), unique=True)
    outcome = Column(String(32), nullable=False)
    approved_amount = Column(Float, nullable=False)
    deductions_amount = Column(Float, nullable=False)
    clause_citations = Column(JSON, default=list)
    fired_rule_ids = Column(JSON, default=list)
    audit_hash = Column(String(64), nullable=False)
    decided_at = Column(DateTime, default=utc_now)
    reviewer_notes = Column(Text, nullable=True)

    claim = relationship("ClaimRecord", back_populates="decision")


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    event_id = Column(String(64), primary_key=True, index=True)
    claim_id = Column(String(64), index=True, nullable=False)
    stage = Column(String(32), nullable=False)
    input_hash = Column(String(64), nullable=False)
    rule_ids_fired = Column(JSON, default=list)
    model_version = Column(String(32), default="v1.0.0")
    duration_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    details = Column(JSON, default=dict)


# Engine and session initialization with automatic SQLite fallback
db_url = settings.DATABASE_URL
if settings.USE_SQLITE_FALLBACK and os.environ.get("ENVIRONMENT") != "production":
    # If not explicitly in Docker/production postgres, use sqlite fallback for local dev
    db_url = settings.SQLITE_FALLBACK_URL

engine = create_async_engine(db_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

