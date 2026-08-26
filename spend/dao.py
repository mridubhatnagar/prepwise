import logging
import uuid
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from sqlalchemy import func, cast, extract, Date
from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError as SADatabaseError

from exceptions import DatabaseError
from infra.postgres import SessionLocal
from spend.models import SpendLog

logger = logging.getLogger(__name__)


class ISpendDAO(ABC):
    @abstractmethod
    def create(
        self,
        visitor_id: str | None,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd: Decimal,
        endpoint: str | None,
    ) -> SpendLog: ...

    @abstractmethod
    def get_total_per_day(self, for_date: date) -> float: ...

    @abstractmethod
    def get_total(self) -> float: ...

    @abstractmethod
    def get_monthly_totals(self) -> list[dict]: ...


class SpendDAO(ISpendDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(
        self,
        visitor_id: str | None,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd: Decimal,
        endpoint: str | None,
    ) -> SpendLog:
        try:
            log = SpendLog(
                id=uuid.uuid4(),
                visitor_id=uuid.UUID(visitor_id) if visitor_id else None,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=estimated_cost_usd,
                endpoint=endpoint,
            )
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            logger.info(
                "SpendLog created: model=%s cost=%.6f visitor_id=%s",
                model, estimated_cost_usd, visitor_id,
            )
            return log
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("SpendDAO.create failed: %s", exc)
            raise DatabaseError("Failed to create spend log") from exc

    def get_total_per_day(self, for_date: date) -> float:
        """Return the sum of estimated_cost_usd for all spend logs on the given date."""
        try:
            total = (
                self.db.query(func.coalesce(func.sum(SpendLog.estimated_cost_usd), 0))
                .filter(cast(SpendLog.logged_at, Date) == for_date)
                .scalar()
            )
            return float(total)
        except (OperationalError, SADatabaseError) as exc:
            logger.error("SpendDAO.get_total_per_day failed for date=%s: %s", for_date, exc)
            raise DatabaseError("Failed to fetch total spend") from exc

    def get_total(self) -> float:
        """Return the sum of estimated_cost_usd across all spend logs."""
        try:
            total = (
                self.db.query(func.coalesce(func.sum(SpendLog.estimated_cost_usd), 0))
                .scalar()
            )
            return float(total)
        except (OperationalError, SADatabaseError) as exc:
            logger.error("SpendDAO.get_total failed: %s", exc)
            raise DatabaseError("Failed to fetch all-time total spend") from exc

    def get_monthly_totals(self) -> list[dict]:
        """Return estimated_cost_usd summed per (year, month) of logged_at, oldest first.

        Each entry: {"year": int, "month": int, "cost": float}.
        """
        try:
            year = extract("year", SpendLog.logged_at)
            month = extract("month", SpendLog.logged_at)
            rows = (
                self.db.query(
                    year.label("year"),
                    month.label("month"),
                    func.coalesce(func.sum(SpendLog.estimated_cost_usd), 0).label("cost"),
                )
                .group_by(year, month)
                .order_by(year, month)
                .all()
            )
            return [
                {"year": int(row.year), "month": int(row.month), "cost": float(row.cost)}
                for row in rows
            ]
        except (OperationalError, SADatabaseError) as exc:
            logger.error("SpendDAO.get_monthly_totals failed: %s", exc)
            raise DatabaseError("Failed to fetch monthly spend totals") from exc
