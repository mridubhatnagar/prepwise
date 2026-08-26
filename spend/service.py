import calendar
import logging
import smtplib
from datetime import date
from decimal import Decimal
from email.mime.text import MIMEText

from config import config
from constants import (
    EMBEDDING_INPUT_COST_PER_1M,
    EMBEDDING_MODEL,
    GPT4O_INPUT_COST_PER_1M,
    GPT4O_OUTPUT_COST_PER_1M,
    LLM_MODEL,
)
from spend.dao import ISpendDAO
from spend.models import SpendLog

logger = logging.getLogger(__name__)

_COST_TABLE: dict[str, dict[str, float]] = {
    LLM_MODEL: {
        "input": GPT4O_INPUT_COST_PER_1M,
        "output": GPT4O_OUTPUT_COST_PER_1M,
    },
    EMBEDDING_MODEL: {
        "input": EMBEDDING_INPUT_COST_PER_1M,
        "output": 0.0,
    },
}


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Return the estimated USD cost for the given token usage.

    Falls back to GPT-4o pricing for unknown models so spend is never
    silently under-reported.
    """
    rates = _COST_TABLE.get(model, _COST_TABLE[LLM_MODEL])
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
    return Decimal(str(round(cost, 6)))


class SpendService:
    def __init__(self, spend_dao: ISpendDAO):
        self.spend_dao = spend_dao

    def create_spend(
        self,
        visitor_id: str | None,
        model: str,
        input_tokens: int,
        output_tokens: int,
        endpoint: str | None,
    ) -> SpendLog:
        """Calculate cost and persist a SpendLog entry."""
        estimated_cost_usd = _calculate_cost(model, input_tokens, output_tokens)
        return self.spend_dao.create(
            visitor_id=visitor_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
            endpoint=endpoint,
        )

    def get_total_spend_per_day(self, for_date: date) -> float:
        return self.spend_dao.get_total_per_day(for_date)

    def get_total_spend(self) -> float:
        return self.spend_dao.get_total()

    def get_monthly_spend_summary(self) -> dict:
        """Return all-time spend grouped by year/month, in the /api/spend/monthly shape.

        Years cover every month since the first spend_logs row (no bounded
        window); the last entry is the current, still-accumulating month.
        """
        totals = self.spend_dao.get_monthly_totals()

        monthly_spend: list[dict] = []
        for entry in totals:
            month_entry = {
                "month": calendar.month_name[entry["month"]],
                "cost": round(entry["cost"], 2),
            }
            if monthly_spend and monthly_spend[-1]["year"] == entry["year"]:
                monthly_spend[-1]["months"].append(month_entry)
            else:
                monthly_spend.append({"year": entry["year"], "months": [month_entry]})

        return {
            "currency": "USD",
            "note": "LLM and embedding API costs only — excludes server/infra costs.",
            "total": round(sum(entry["cost"] for entry in totals), 2),
            "monthly_spend": monthly_spend,
        }
    def is_daily_cap_exceeded(self) -> bool:
        """Return True if today's total spend has reached the configured hard cap.

        Returns False when ``DAILY_SPEND_CAP_USD`` is unset, so chat is never
        blocked by an unconfigured cap. This is a hard, blocking check —
        distinct from ``spend_email_alert``'s notify-only crossing-point
        alert, which remains unchanged.
        """
        cap = config.DAILY_SPEND_CAP_USD
        if cap is None:
            return False

        today_total = self.get_total_spend_per_day(date.today())
        exceeded = today_total >= cap
        if exceeded:
            logger.warning(
                "Daily spend cap exceeded: today_total=%.4f cap=%.2f", today_total, cap
            )
        return exceeded

    def spend_email_alert(self, current_cost: Decimal) -> None:
        """Send a spend alert email if the cumulative threshold has just been crossed.

        Computes the all-time total before this transaction by subtracting
        current_cost. Sends an alert only on the first crossing — when the
        previous total was below the threshold and the current total is at or
        above it.

        SMTP failures are caught and logged — they must not surface to the
        caller or roll back the spend log.
        """
        threshold = config.SPEND_ALERT_THRESHOLD
        all_time_total = self.get_total_spend()
        previous_total = all_time_total - float(current_cost)

        if not (previous_total < threshold <= all_time_total):
            return

        logger.info(
            "Spend threshold crossed: previous=%.4f current=%.4f threshold=%.4f",
            previous_total,
            all_time_total,
            threshold,
        )

        self._send_alert_email(all_time_total, threshold)

    def _send_alert_email(self, all_time_total: float, threshold: float) -> None:
        """Send the threshold-crossed alert via SMTP."""
        subject = f"[PrepWise] Cumulative spend alert — ${all_time_total:.4f}"
        body = (
            f"PrepWise spend alert\n\n"
            f"Cumulative spend: ${all_time_total:.4f}\n"
            f"Threshold: ${threshold:.2f}\n\n"
            f"Review spend logs to identify high-cost sessions."
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = config.SMTP_USER
        msg["To"] = config.ALERT_EMAIL

        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
                smtp.sendmail(config.SMTP_USER, [config.ALERT_EMAIL], msg.as_string())
            logger.info(
                "Spend alert email sent to %s (total=%.4f threshold=%.2f)",
                config.ALERT_EMAIL,
                all_time_total,
                threshold,
            )
        except smtplib.SMTPException as exc:
            logger.error("Failed to send spend alert email: %s", exc)
