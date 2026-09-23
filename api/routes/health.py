from fastapi import APIRouter, status

router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    """Return the current API health status."""
    return {
        "status": "healthy",
    }
