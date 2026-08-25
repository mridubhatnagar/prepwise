import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import verify_docs_credentials
from exceptions import DatabaseError
from spend.dao import ISpendDAO, SpendDAO
from spend.service import SpendService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["spend"])


class MonthSpend(BaseModel):
    month: str
    cost: float


class YearlySpend(BaseModel):
    year: int
    months: list[MonthSpend]


class MonthlySpendData(BaseModel):
    currency: str
    note: str
    total: float
    monthly_spend: list[YearlySpend]


def get_spend_dao() -> ISpendDAO:
    return SpendDAO()


def get_spend_service(
    spend_dao: ISpendDAO = Depends(get_spend_dao),
) -> SpendService:
    return SpendService(spend_dao=spend_dao)


@router.get("/api/spend/monthly")
async def get_monthly_spend(
    credentials: None = Depends(verify_docs_credentials),
    spend_service: SpendService = Depends(get_spend_service),
):
    """Return all-time LLM/embedding spend grouped by year and month.

    Owner-only visibility into cost trends — gated by the same HTTP Basic
    Auth credentials as /docs, kept separate from the anonymous chat surface.
    """
    try:
        summary = spend_service.get_monthly_spend_summary()
    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Something went wrong. Please try again.",
        )

    data = MonthlySpendData(**summary)
    return {"success": True, "data": data.model_dump(), "error": None}
