"""HikCentral OpenAPI models."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict


class ResponseData(BaseModel):
    """Response data model."""

    model_config = ConfigDict(populate_by_name=True)
    total: int
    page_size: int | None = Field(None, alias="pageSize")
    page_no: int | None = Field(None, alias="pageNo")
    result: list[dict[str, Any]] = Field(default_factory=list, alias="list")


class APIResponse(TypedDict):
    """API response model."""

    code: str
    msg: str
    data: Any


class ProductVersion(BaseModel):
    """Product version model."""

    model_config = ConfigDict(populate_by_name=True)
    produce_name: str = Field(..., alias="produceName")
    soft_version: str = Field(..., alias="softVersion")


class ResourceEndpoint(StrEnum):
    """Resource endpoints."""

    VERSION_INFO = "/artemis/api/common/v1/version"
    BASE_URL = "/artemis/api/resource/v1"
    ORG_LIST = f"{BASE_URL}/org/advance/orgList"
    ORG_ROOT = f"{BASE_URL}/org/rootOrg"
    ORG_ADD = f"{BASE_URL}/org/single/add"
    ORG_UPDATE = f"{BASE_URL}/org/single/update"
    ORG_DELETE = f"{BASE_URL}/org/single/delete"
    PERSON_INFO = f"{BASE_URL}/person/personId/personInfo"
    PERSON_LIST = f"{BASE_URL}/person/advance/personList"
    PERSON_ADD = f"{BASE_URL}/person/single/add"
    PERSON_UPDATE = f"{BASE_URL}/person/single/update"
    PERSON_FACE_UPDATE = f"{BASE_URL}/person/face/update"
    PERSON_DELETE = f"{BASE_URL}/person/single/delete"


class Organization(BaseModel):
    """Organization model."""

    model_config = ConfigDict(populate_by_name=True)
    org_id: str = Field(..., alias="orgIndexCode")
    org_name: str = Field(..., alias="orgName")
    parent_org_id: str = Field(..., alias="parentOrgIndexCode")

    def update_dict(self) -> dict[str, Any]:
        """Organization update dict."""
        return {
            "orgName": self.org_name,
            "orgIndexCode": self.org_id,
            "parentIndexCode": self.parent_org_id,
        }


class PersonFingerPrint(BaseModel):
    """Person fingerprint model."""

    finger_print_index_code: str | None = Field(None, alias="fingerPrintIndexCode")
    finger_print_name: str | None = Field(None, alias="fingerPrintName")
    finger_print_data: str | None = Field(None, alias="fingerPrintData")
    related_card_no: str | None = Field(None, alias="relatedCardNo")


class PersonPhoto(TypedDict):
    """Person photo dict."""

    picUri: str


class Card(BaseModel):
    """Card model."""

    model_config = ConfigDict(populate_by_name=True)
    card_no: str = Field(..., alias="cardNo")


class Face(BaseModel):
    """Face model."""

    model_config = ConfigDict(populate_by_name=True)
    face_data: str = Field(..., alias="faceData")


class CustomField(BaseModel):
    """Custom field model."""

    model_config = ConfigDict(populate_by_name=True)
    id: str | None = Field(None)
    custom_field_name: str | None = Field(None, alias="customFieldName")
    custom_field_type: int | None = Field(None, alias="customFieldType")
    custom_field_value: str | None = Field(None, alias="customFieldValue")
    preset_value_list: list[dict[str, Any]] | None = Field(
        None, alias="presetValueList"
    )
    is_public: bool = Field(False, alias="isPublic")
    is_show: bool = Field(True, alias="isShow")


class Person(BaseModel):
    """Person model."""

    model_config = ConfigDict(populate_by_name=True)
    person_id: str | None = Field(None, alias="personId")
    person_code: str | None = Field(None, alias="personCode")
    person_name: str | None = Field(None, alias="personName")
    person_family_name: str | None = Field(None, alias="personFamilyName")
    person_given_name: str | None = Field(None, alias="personGivenName")
    gender: int | None = Field(None)
    org_index_code: str | None = Field(None, alias="orgIndexCode")
    finger_print: PersonFingerPrint | None = Field(None, alias="fingerPrint")
    phone_no: str | None = Field(None, alias="phoneNo")
    person_photo: PersonPhoto | None = Field(None, alias="personPhoto")
    email: str | None = Field(None)
    remark: str | None = Field(None)
    cards: list[Card] = Field(default_factory=list)
    faces: list[Face] = Field(default_factory=list)
    begin_time: datetime | None = Field(None, alias="beginTime")
    end_time: datetime | None = Field(None, alias="endTime")
    custom_field_list: list[CustomField] | None = Field(None, alias="customFieldList")

    def update_dict(self) -> dict[str, Any]:
        """Person update dict."""
        return {
            "personId": self.person_id,
            "personName": self.person_name,
            "personFamilyName": self.person_family_name,
            "personGivenName": self.person_given_name,
            "orgIndexCode": self.org_index_code,
            "phoneNo": self.phone_no,
            "email": self.email,
            "cards": [{"cardNo": card.card_no} for card in self.cards],
        }
