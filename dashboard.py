"""
FastAPI dashboard endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database.models import Database

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crypto Smart Money Agent API",
    description="API for monitoring trading signals and performance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Crypto Smart Money Agent"
    }


@app.get("/api/signals")
async def get_recent_signals(limit: int = 20):
    """Get recent signals"""
    try:
        signals = db.get_recent_signals(limit=limit)
        return {
            "status": "success",
            "count": len(signals),
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error fetching signals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


@app.get("/api/signals/{signal_id}")
async def get_signal_details(signal_id: int):
    """Get specific signal details"""
    try:
        signal = db.get_signal_by_id(signal_id)
        if signal is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        return {
            "status": "success",
            "signal": signal
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch signal")


@app.get("/api/stats")
async def get_statistics():
    """Get overall statistics"""
    try:
        stats = db.get_performance_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@app.get("/api/signals/status/{status}")
async def get_signals_by_status(status: str, limit: int = 50):
    """Get signals filtered by status"""
    try:
        if status not in ["open", "closed", "rug_pull"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        signals = db.get_recent_signals(limit=limit)
        filtered = [s for s in signals if s.get('status') == status]
        
        return {
            "status": "success",
            "count": len(filtered),
            "signals": filtered
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


@app.post("/api/signals/{signal_id}/close")
async def close_signal(signal_id: int, status: str = "closed"):
    """Close/resolve a signal"""
    try:
        if status not in ["closed", "rug_pull"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        signal = db.get_signal_by_id(signal_id)
        if signal is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        db.update_signal_status(signal_id, status)
        
        return {
            "status": "success",
            "message": f"Signal {signal_id} marked as {status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating signal: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update signal")


@app.get("/api/metrics")
async def get_metrics():
    """Get key performance metrics"""
    try:
        stats = db.get_performance_stats()
        
        return {
            "status": "success",
            "metrics": {
                "total_signals": stats["total_signals"],
                "winning_signals": stats["winners"],
                "win_rate_percent": stats["win_rate"],
                "average_bullish_score": stats["avg_bullish_score"],
                "average_confidence_score": stats["avg_confidence_score"],
                "average_risk_score": stats["avg_risk_score"]
            }
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate metrics")


@app.get("/api/chains")
async def get_chains():
    """Get list of chains with signals"""
    try:
        signals = db.get_recent_signals(limit=1000)
        chains = set(s.get('chain') for s in signals if s.get('chain'))
        
        return {
            "status": "success",
            "chains": sorted(list(chains)),
            "count": len(chains)
        }
    except Exception as e:
        logger.error(f"Error fetching chains: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chains")


@app.get("/api/top-performers")
async def get_top_performers(limit: int = 10):
    """Get top performing signals"""
    try:
        signals = db.get_recent_signals(limit=1000)
        
        # Sort by bullish score
        sorted_signals = sorted(
            signals,
            key=lambda x: x.get('ai_bullish_score', 0),
            reverse=True
        )
        
        return {
            "status": "success",
            "count": min(limit, len(sorted_signals)),
            "signals": sorted_signals[:limit]
        }
    except Exception as e:
        logger.error(f"Error fetching top performers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch top performers")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
