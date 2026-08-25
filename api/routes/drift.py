"""
FastAPI route for feature drift, prediction drift, and residual monitoring.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status

from api.schemas import DriftReportResponse
from src.services.monitoring_service import MonitoringService
from src.utils.logger import get_logger

logger = get_logger("api.routes.drift")
drift_router = APIRouter(tags=["Monitoring & Drift"])

# Singleton MonitoringService instance
_monitoring_service = MonitoringService()


@drift_router.get(
    "/drift",
    response_model=DriftReportResponse,
    summary="Get Model Drift & Residual Health Report",
    description=(
        "Calculates Population Stability Index (PSI), Kolmogorov-Smirnov (KS) test, "
        "prediction distribution shift, and forecast bias tracking across key demand features."
    ),
)
async def get_drift_report():
    """
    Returns current model drift metrics, PSI feature stability scores, and residual health status.
    """
    try:
        report = _monitoring_service.get_drift_report()
        now_utc = datetime.now(timezone.utc).isoformat()

        return DriftReportResponse(
            status="success",
            overall_status=report.overall_status,
            summary_message=report.summary_message,
            feature_drift={
                k: v.model_dump() for k, v in report.feature_drift.items()
            },
            prediction_drift=report.prediction_drift.model_dump() if report.prediction_drift else None,
            residual_analysis=report.residual_analysis.model_dump() if report.residual_analysis else None,
            timestamp=now_utc,
        )
    except Exception as e:
        logger.error(f"Failed to generate drift report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating drift report: {str(e)}",
        ) from e
