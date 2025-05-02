from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import engine, Base
from config import settings
from utils.metrics import start_metrics_server, track_request_latency
from utils.kafka import kafka_manager, TOPICS


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start metrics server
    start_metrics_server(port=8001)

    yield

    # Clean up resources
    kafka_manager.producer.close()


app = FastAPI(
    title="Enterprise Manager API",
    description="API for Enterprise Manager application",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@track_request_latency(method="GET", endpoint="/")
async def root():
    return JSONResponse(
        content={"message": "Welcome to Enterprise Manager API"}, status_code=200
    )


# Import and include routers
from routers import auth, clients, orders, tasks

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
