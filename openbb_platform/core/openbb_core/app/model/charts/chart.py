from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChartFormat(str, Enum):
    plotly = "plotly"


class Chart(BaseModel):
    content: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw textual representation of the chart.",
    )
    format: Optional[ChartFormat] = Field(
        default=ChartFormat.plotly,
        description="Complementary attribute to the `content` attribute. It specifies the format of the chart.",
    )
    fig: Optional[Any] = Field(
        default=None,
        description="The figure object.",
        json_schema_extra={"exclude_from_api": True},
    )
    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
