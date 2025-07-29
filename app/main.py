from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from app.core.config import settings
from app.core.database import engine, Base
from app.routes import auth, wallet, alias, admin, currency, notification, pin
from app.utils.logging import setup_logging

# Create database tables (commented out for testing without database)
# Base.metadata.create_all(bind=engine)

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="DARI Wallet Backend",
    description="Semi-custodial Multi-chain Blockchain Wallet API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on your deployment
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(wallet.router, prefix="/api/v1")
app.include_router(alias.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(currency.router, prefix="/api/v1")
app.include_router(notification.router, prefix="/api/v1")
app.include_router(pin.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DARI Wallet Backend"}


# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "DARI Wallet Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logging.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 