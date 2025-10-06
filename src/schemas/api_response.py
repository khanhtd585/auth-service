from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(
        False,
        description="Indicate if the request is successfully handled or not",
        examples=[True],
    )
    data: Optional[T] = Field(
        None,
        description="Return data. If the request is successfully handled, it should be the returned data of the endpoint, otherwise the error details",
    )
    message: Optional[str] = Field(
        None, description="Short message related to the error", examples=[None]
    )
