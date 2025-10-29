"""
Backend API for TotalCare AI Partner Portal
Provides secure access to Autotask and HubSpot data
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    # Try relative imports first (when running via uvicorn api.main:app)
    from api.autotask_service import (
        get_autotask_client,
        get_reporting_service,
        AutotaskClient,
        AutotaskReportingService
    )
    from api.hubspot_service import (
        get_hubspot_client,
        get_hubspot_reporting_service,
        HubSpotClient,
        HubSpotReportingService
    )
    from api.datto_service import (
        get_datto_commerce_client,
        get_datto_rmm_client,
        get_datto_reporting_service,
        DattoCommerceClient,
        DattoRMMClient,
        DattoReportingService
    )
    from api.connectwise_service import (
        get_connectwise_client,
        get_connectwise_reporting_service,
        ConnectWiseManageClient,
        ConnectWiseReportingService
    )
    from api.microsoft365_service import (
        get_microsoft365_client,
        get_microsoft365_reporting_service,
        Microsoft365Client,
        Microsoft365ReportingService
    )
except ModuleNotFoundError:
    # Fall back to direct imports (when running python3 api/main.py directly)
    from autotask_service import (
        get_autotask_client,
        get_reporting_service,
        AutotaskClient,
        AutotaskReportingService
    )
    from hubspot_service import (
        get_hubspot_client,
        get_hubspot_reporting_service,
        HubSpotClient,
        HubSpotReportingService
    )
    from datto_service import (
        get_datto_commerce_client,
        get_datto_rmm_client,
        get_datto_reporting_service,
        DattoCommerceClient,
        DattoRMMClient,
        DattoReportingService
    )
    from connectwise_service import (
        get_connectwise_client,
        get_connectwise_reporting_service,
        ConnectWiseManageClient,
        ConnectWiseReportingService
    )
    from microsoft365_service import (
        get_microsoft365_client,
        get_microsoft365_reporting_service,
        Microsoft365Client,
        Microsoft365ReportingService
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TotalCare AI Partner Portal API",
    description="Backend API for HubSpot, Autotask, Datto, ConnectWise, and Microsoft 365 integration",
    version="2.0.0"
)

# Configure CORS for frontend
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://totalcareit.ai,http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TotalCare AI Partner Portal API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "checks": {
            "autotask": "unchecked",
            "hubspot": "unchecked",
            "datto_commerce": "unchecked",
            "datto_rmm": "unchecked",
            "connectwise": "unchecked",
            "microsoft365": "unchecked"
        }
    }

    # Check Autotask connection
    try:
        client = get_autotask_client()
        if client.is_configured():
            health_status["checks"]["autotask"] = "configured"
        else:
            health_status["checks"]["autotask"] = "not_configured"
    except Exception as e:
        logger.error(f"Autotask health check failed: {e}")
        health_status["checks"]["autotask"] = "error"

    # Check HubSpot configuration
    try:
        client = get_hubspot_client()
        if client.is_configured():
            health_status["checks"]["hubspot"] = "configured"
        else:
            health_status["checks"]["hubspot"] = "not_configured"
    except Exception as e:
        logger.error(f"HubSpot health check failed: {e}")
        health_status["checks"]["hubspot"] = "error"

    # Check Datto Commerce
    try:
        client = get_datto_commerce_client()
        if client.is_configured():
            health_status["checks"]["datto_commerce"] = "configured"
        else:
            health_status["checks"]["datto_commerce"] = "not_configured"
    except Exception as e:
        logger.error(f"Datto Commerce health check failed: {e}")
        health_status["checks"]["datto_commerce"] = "error"

    # Check Datto RMM
    try:
        client = get_datto_rmm_client()
        if client.is_configured():
            health_status["checks"]["datto_rmm"] = "configured"
        else:
            health_status["checks"]["datto_rmm"] = "not_configured"
    except Exception as e:
        logger.error(f"Datto RMM health check failed: {e}")
        health_status["checks"]["datto_rmm"] = "error"

    # Check ConnectWise
    try:
        client = get_connectwise_client()
        if client.is_configured():
            health_status["checks"]["connectwise"] = "configured"
        else:
            health_status["checks"]["connectwise"] = "not_configured"
    except Exception as e:
        logger.error(f"ConnectWise health check failed: {e}")
        health_status["checks"]["connectwise"] = "error"

    # Check Microsoft 365
    try:
        client = get_microsoft365_client()
        if client.is_configured():
            health_status["checks"]["microsoft365"] = "configured"
        else:
            health_status["checks"]["microsoft365"] = "not_configured"
    except Exception as e:
        logger.error(f"Microsoft 365 health check failed: {e}")
        health_status["checks"]["microsoft365"] = "error"

    return health_status


# ===== AUTOTASK ENDPOINTS =====

@app.get("/api/autotask/tickets")
async def get_tickets(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    service: AutotaskReportingService = Depends(get_reporting_service)
):
    """
    Get ROC board tickets with optional date filtering

    Returns ticket metrics and list of tickets from the ROC (Reactive Services) board only.
    """
    try:
        # Parse dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        metrics = service.get_ticket_metrics(start, end)

        return JSONResponse(content={
            "success": True,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch tickets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tickets: {str(e)}")


@app.get("/api/autotask/activity")
async def get_activity(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    service: AutotaskReportingService = Depends(get_reporting_service)
):
    """
    Get activity summary for ROC board tickets

    Returns summary of ticket activity including time entries and hours logged.
    """
    try:
        # Parse dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        summary = service.get_activity_summary(start, end)

        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity: {str(e)}")


@app.get("/api/autotask/report/daily")
async def get_daily_report(
    date: Optional[str] = Query(None, description="Date for report (ISO format, default: today)"),
    service: AutotaskReportingService = Depends(get_reporting_service)
):
    """
    Get daily ticket report for ROC board

    Returns metrics for a single day.
    """
    try:
        # Parse date or use today
        if date:
            report_date = datetime.fromisoformat(date)
        else:
            report_date = datetime.now()

        # Set date range for the day
        start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        metrics = service.get_ticket_metrics(start, end)
        activity = service.get_activity_summary(start, end)

        return JSONResponse(content={
            "success": True,
            "date": report_date.date().isoformat(),
            "metrics": metrics,
            "activity": activity,
            "timestamp": datetime.now().isoformat()
        })

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@app.get("/api/autotask/report/monthly")
async def get_monthly_report(
    year: Optional[int] = Query(None, description="Year for report (default: current year)"),
    month: Optional[int] = Query(None, description="Month for report (1-12, default: current month)"),
    service: AutotaskReportingService = Depends(get_reporting_service)
):
    """
    Get monthly ticket report for ROC board

    Returns metrics for an entire month.
    """
    try:
        now = datetime.now()
        report_year = year or now.year
        report_month = month or now.month

        # Validate month
        if not 1 <= report_month <= 12:
            raise ValueError("Month must be between 1 and 12")

        # Calculate date range for month
        start = datetime(report_year, report_month, 1)
        if report_month == 12:
            end = datetime(report_year + 1, 1, 1)
        else:
            end = datetime(report_year, report_month + 1, 1)

        metrics = service.get_ticket_metrics(start, end)
        activity = service.get_activity_summary(start, end)

        return JSONResponse(content={
            "success": True,
            "year": report_year,
            "month": report_month,
            "metrics": metrics,
            "activity": activity,
            "timestamp": datetime.now().isoformat()
        })

    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to generate monthly report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


# ===== HUBSPOT ENDPOINTS =====

@app.get("/api/hubspot/crm/summary")
async def get_crm_summary(
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get CRM summary statistics from HubSpot

    Returns counts of contacts, deals, and companies.
    """
    try:
        summary = service.get_crm_summary()

        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch HubSpot CRM summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch CRM summary: {str(e)}")


@app.get("/api/hubspot/contacts/recent")
async def get_recent_contacts(
    limit: int = Query(10, description="Number of recent contacts to return"),
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get recently created or modified contacts

    Returns list of recent contacts with basic information.
    """
    try:
        contacts = service.get_recent_contacts(limit)

        return JSONResponse(content={
            "success": True,
            "data": contacts,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch recent contacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch contacts: {str(e)}")


@app.get("/api/hubspot/deals/pipeline")
async def get_deals_pipeline(
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get sales pipeline from HubSpot deals

    Returns deals grouped by stage with total values.
    """
    try:
        pipeline = service.get_deal_pipeline()

        return JSONResponse(content={
            "success": True,
            "data": pipeline,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch deals pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch pipeline: {str(e)}")


@app.get("/api/hubspot/analytics")
async def get_analytics(
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get website analytics from HubSpot

    Returns page views, sessions, and other web metrics.
    """
    try:
        analytics = service.get_website_analytics()

        return JSONResponse(content={
            "success": True,
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")


@app.get("/api/hubspot/forms")
async def get_forms_stats(
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get form submission statistics from HubSpot

    Returns list of forms with submission counts.
    """
    try:
        forms = service.get_form_stats()

        return JSONResponse(content={
            "success": True,
            "data": forms,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch form stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch forms: {str(e)}")


@app.get("/api/hubspot/sales-metrics")
async def get_sales_metrics(
    service: HubSpotReportingService = Depends(get_hubspot_reporting_service)
):
    """
    Get sales metrics for sales report dashboard

    Returns calls, meetings, and pipeline metrics formatted for sales report.
    """
    try:
        metrics = service.get_sales_metrics()

        return JSONResponse(content={
            "success": True,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch sales metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


# ===== SCORECARD ENDPOINTS =====

@app.get("/api/scorecard/weekly")
async def get_weekly_scorecard(
    week_start: str = Query(..., description="Week start date (YYYY-MM-DD format, Monday)"),
    autotask_service: AutotaskReportingService = Depends(get_reporting_service)
):
    """
    Get weekly scorecard metrics for all boards (ROC, Pro Services, TAM, Sales)

    Returns tickets opened, closed, same-day close rate for the specified week
    """
    try:
        from datetime import datetime, timedelta
        try:
            from api.autotask_service import get_autotask_client
        except ModuleNotFoundError:
            from autotask_service import get_autotask_client

        # Parse dates
        start_date = datetime.fromisoformat(week_start)
        end_date = start_date + timedelta(days=6)  # Sunday

        logger.info(f"Getting scorecard for week {week_start} to {end_date.date()}")

        client = get_autotask_client()

        # Get ROC tickets for the week
        roc_tickets = autotask_service.get_roc_tickets_for_period(start_date, end_date)

        # Calculate ROC metrics
        roc_opened = len(roc_tickets)
        roc_closed = sum(1 for t in roc_tickets if t.get('completedDate'))

        # Same-day close calculation for ROC
        roc_same_day_closed = 0
        for ticket in roc_tickets:
            if ticket.get('completedDate') and ticket.get('createDate'):
                create_dt = datetime.fromisoformat(ticket['createDate'].replace('Z', '+00:00'))
                complete_dt = datetime.fromisoformat(ticket['completedDate'].replace('Z', '+00:00'))
                if create_dt.date() == complete_dt.date():
                    roc_same_day_closed += 1

        # Calculate rate
        same_day_rate = (roc_same_day_closed / roc_closed * 100) if roc_closed > 0 else 0

        # Determine status vs goal
        goal = 70.0
        if same_day_rate >= goal:
            status = "above_goal"
        elif same_day_rate >= goal * 0.9:
            status = "near_goal"
        else:
            status = "below_goal"

        # Get Pro Services tickets COMPLETED during the week
        # Note: Pro Services tracks by completion date, not creation date
        pro_services_tickets = []
        if client.PRO_SERVICES_QUEUE_ID:
            filters = {
                'filter': [
                    {'field': 'queueID', 'op': 'eq', 'value': int(client.PRO_SERVICES_QUEUE_ID)},
                    {'field': 'completedDate', 'op': 'gte', 'value': start_date.isoformat()},
                    {'field': 'completedDate', 'op': 'lte', 'value': end_date.isoformat()}
                ],
                'MaxRecords': 500
            }
            result = client.query('/Tickets/query', filters)
            pro_services_tickets = result.get('items', [])

        # Get TAM tickets for the week
        tam_tickets = []
        if client.TAM_QUEUE_ID:
            tam_tickets = client.get_tickets_by_queue(
                int(client.TAM_QUEUE_ID),
                start_date,
                end_date
            )

        # Get currently open Sales tickets (no date filter)
        sales_open_tickets = []
        if client.SALES_QUEUE_ID:
            sales_open_tickets = client.get_tickets_by_queue(
                int(client.SALES_QUEUE_ID),
                only_open=True
            )

        return JSONResponse(content={
            "success": True,
            "data": {
                "week_start": week_start,
                "week_end": end_date.strftime('%Y-%m-%d'),
                "roc": {
                    "tickets_opened": roc_opened,
                    "tickets_closed": roc_closed,
                    "same_day_closed": roc_same_day_closed,
                    "same_day_close_rate": round(same_day_rate, 1),
                    "goal": goal,
                    "status": status,
                    "gap": round(same_day_rate - goal, 1)
                },
                "pro_services": {
                    "tickets_completed": len(pro_services_tickets)  # All returned tickets are completed (filtered by completedDate)
                },
                "tam": {
                    "tickets_opened": len(tam_tickets),
                    "tickets_closed": sum(1 for t in tam_tickets if t.get('completedDate'))
                },
                "sales": {
                    "currently_open": len(sales_open_tickets)
                },
                "utilization": None,  # TODO: Calculate from time entries
                "vcio_reviews": None  # TODO: Manual input needed
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get weekly scorecard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scorecard: {str(e)}")


# ===== DATTO ENDPOINTS =====

@app.get("/api/datto/commerce/summary")
async def get_datto_commerce_summary(
    service: DattoReportingService = Depends(get_datto_reporting_service)
):
    """Get sales summary from Datto Commerce (quotes/opportunities)"""
    try:
        summary = service.get_sales_summary()
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch Datto Commerce summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datto/rmm/summary")
async def get_datto_rmm_summary(
    service: DattoReportingService = Depends(get_datto_reporting_service)
):
    """Get RMM summary from Datto RMM (devices/alerts)"""
    try:
        summary = service.get_rmm_summary()
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch Datto RMM summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== CONNECTWISE ENDPOINTS =====

@app.get("/api/connectwise/sales/summary")
async def get_connectwise_sales_summary(
    service: ConnectWiseReportingService = Depends(get_connectwise_reporting_service)
):
    """Get sales summary from ConnectWise (opportunities)"""
    try:
        summary = service.get_sales_summary()
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch ConnectWise sales summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connectwise/service/summary")
async def get_connectwise_service_summary(
    service: ConnectWiseReportingService = Depends(get_connectwise_reporting_service)
):
    """Get service ticket summary from ConnectWise"""
    try:
        summary = service.get_service_summary()
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch ConnectWise service summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connectwise/time/summary")
async def get_connectwise_time_summary(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    service: ConnectWiseReportingService = Depends(get_connectwise_reporting_service)
):
    """Get time entry summary from ConnectWise"""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        summary = service.get_time_summary(start, end)
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch ConnectWise time summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MICROSOFT 365 ENDPOINTS =====

@app.get("/api/microsoft365/tenant/summary")
async def get_m365_tenant_summary(
    service: Microsoft365ReportingService = Depends(get_microsoft365_reporting_service)
):
    """Get Microsoft 365 tenant summary (users/groups/licenses)"""
    try:
        summary = service.get_tenant_summary()
        return JSONResponse(content={
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch Microsoft 365 tenant summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/microsoft365/licenses")
async def get_m365_licenses(
    service: Microsoft365ReportingService = Depends(get_microsoft365_reporting_service)
):
    """Get Microsoft 365 license details"""
    try:
        licenses = service.get_license_details()
        return JSONResponse(content={
            "success": True,
            "data": licenses,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to fetch Microsoft 365 licenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
