from typing import Any, Optional

from pydantic import BaseModel, Field


class PersonDetails(BaseModel):
    case_id: str
    full_name: str
    contact_info: str
    reporter_address: str
    missing_address: str
    image_url: str


class SearchSuccessMatch(BaseModel):
    status: str = "success"
    match_found: bool = True
    confidence: float = Field(ge=0.0, le=1.0)
    person_details: PersonDetails
    distance: float
    ranked_matches: list[dict[str, Any]] = Field(default_factory=list)


class SearchSuccessNoMatch(BaseModel):
    status: str = "success"
    match_found: bool = False
    message: str = "No matching record found in the database."


class SearchError(BaseModel):
    status: str = "error"
    message: str
