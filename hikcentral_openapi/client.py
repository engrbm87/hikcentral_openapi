"""HikCentral Open Api python library."""

import base64
import hashlib
import hmac
from json import JSONDecodeError
import logging
from ssl import SSLError
from typing import Any, cast

import httpx

from .exceptions import ConnectError, RequestError, UnauthorizedError
from .models import (
    APIResponse,
    Organization,
    Person,
    ProductVersion,
    ResourceEndpoint,
    ResponseData,
)

_LOGGER = logging.getLogger(__name__)


class Client:
    """HikCentral OpenApi client."""

    def __init__(
        self,
        *,
        user_key: str,
        user_secret: str,
        host: str = "localhost",
        port: int = 443,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize REST api client."""
        self.server_url = f"https://{host}:{port}"
        self.httpx_client: httpx.AsyncClient = httpx_client or httpx.AsyncClient(
            verify=False
        )
        self.user_secret = user_secret.encode("UTF-8")
        self.httpx_client.headers = httpx.Headers(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-ca-key": user_key,
                "x-ca-signature-headers": "x-ca-key",
            }
        )
        self.headers_string = (
            f"POST\napplication/json\napplication/json\nx-ca-key:{user_key}"
        )
        self.httpx_client.timeout.read = 60
        self.version: str | None = None

    def generate_hmac_sha256_signature(self, url: str) -> str:
        """
        Generates an HMAC-SHA256 signature.

        Args:
            url: The URL to be signed.
            secret: The secret key (as a string).
        Returns:
            The Base64 encoded HMAC-SHA256 signature (as a string), or None on error.
        """
        string_to_sign_bytes = f"{self.headers_string}\n{url}".encode(
            "UTF-8"
        )  # Encode string to sign to bytes

        hmac_obj = hmac.new(self.user_secret, string_to_sign_bytes, hashlib.sha256)
        signature_bytes = hmac_obj.digest()  # Get the raw signature bytes

        return base64.b64encode(signature_bytes).decode(
            "UTF-8"
        )  # Base64 encode and decode to string

    async def _async_request(
        self,
        endpoint: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        return_list: bool = False,
        page_number: int = 1,
    ) -> Any:
        """Send a http request and return the response."""
        # params = params or {}
        # _LOGGER.debug(
        #     "Sending POST request to endpoint: %s, data: %s, params: %s",
        #     endpoint,
        #     data,
        #     params,
        # )
        signature = self.generate_hmac_sha256_signature(endpoint)
        data = data or {}
        if return_list:
            data.update({"pageNo": page_number, "pageSize": 500})
        try:
            response = await self.httpx_client.request(
                "POST",
                f"{self.server_url}{endpoint}",
                params=params,
                json=data,
                headers={"X-ca-signature": signature},
            )
        except (httpx.RequestError, SSLError) as err:
            raise ConnectError(
                f"Connection failed while sending request: {err}"
            ) from err
        _LOGGER.debug(
            "status_code: %s, response: %s", response.status_code, response.text
        )
        if httpx.codes.is_error(response.status_code):
            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise UnauthorizedError(
                    "Unauthorized request. Ensure api key is correct"
                )
            if response.status_code == httpx.codes.NOT_FOUND:
                message = (
                    "Requested item does not exist or "
                    "your operator does not have the privilege to view it"
                )
            elif response.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                message = "Service Unavailable"
            else:
                try:
                    message = cast(dict[str, Any], response.json()).get(
                        "msg", "Invalid operation"
                    )
                except JSONDecodeError:
                    message = "Unknown error"
            raise RequestError(message)
        # if response.status_code == httpx.codes.CREATED:
        #     return {"location": response.headers.get("location")}
        # if response.status_code == httpx.codes.NO_CONTENT:
        #     return None
        result = cast(APIResponse, response.json())
        if result["code"] != "0":
            raise RequestError(result["msg"])
        return result["data"]

    async def initialize(self) -> None:
        """Connect to Server and initialize data."""
        version = ProductVersion.model_validate(
            await self._async_request(ResourceEndpoint.VERSION_INFO)
        )
        self.version = version.soft_version
        _LOGGER.debug("Initialized client with version: %s", self.version)

    async def get_organization(self, name: str | None = None) -> list[Organization]:
        """Return list of organizations."""
        resp_data = ResponseData.model_validate(
            await self._async_request(
                ResourceEndpoint.ORG_LIST,
                data={"orgName": name} if name else None,
                return_list=True,
            )
        )
        if resp_data.total == 0:
            return []
        return [Organization.model_validate(org) for org in resp_data.result]

    async def get_root_organization(self) -> Organization:
        """Return the root organization."""
        return Organization.model_validate(
            await self._async_request(ResourceEndpoint.ORG_ROOT),
        )

    async def add_organization(
        self, name: str, parent_id: str | None = None
    ) -> Organization:
        """Add a new organization."""
        if parent_id is None:
            parent_org = await self.get_root_organization()
            parent_id = parent_org.org_id
        return Organization.model_validate(
            await self._async_request(
                ResourceEndpoint.ORG_ADD,
                data={"orgName": name, "parentIndexCode": parent_id},
            )
        )

    async def update_organization(self, org: Organization) -> None:
        """Update an existing organization."""
        await self._async_request(ResourceEndpoint.ORG_UPDATE, data=org.update_dict())

    async def delete_organization(self, org_id: str) -> None:
        """Delete an organization."""
        await self._async_request(
            ResourceEndpoint.ORG_DELETE, data={"orgIndexCode": org_id}
        )

    async def get_person(
        self,
        *,
        person_id: str | None = None,
        name: str | None = None,
        card_no: str | None = None,
    ) -> list[Person]:
        """Return list of persons based on search params."""
        if person_id:
            return [
                Person.model_validate(
                    await self._async_request(
                        ResourceEndpoint.PERSON_INFO,
                        data={"personId": person_id},
                    )
                )
            ]
        persons: list[Person] = []
        page_number = 1
        data = {}
        if name:
            data["personName"] = name
        if card_no:
            data["cardNo"] = card_no
        while True:
            resp_data = ResponseData.model_validate(
                await self._async_request(
                    ResourceEndpoint.PERSON_LIST,
                    return_list=True,
                    page_number=page_number,
                    data=data,
                )
            )
            if resp_data.total == 0:
                break
            persons += [Person.model_validate(person) for person in resp_data.result]
            if len(persons) >= resp_data.total:
                break
            page_number += 1
        return persons

    async def add_person(self, person: Person) -> str:
        """Add a new person."""
        return await self._async_request(
            ResourceEndpoint.PERSON_ADD,
            data=person.model_dump(by_alias=True, exclude_none=True),
        )

    async def update_person(self, person: Person) -> None:
        """Update an existing person."""
        await self._async_request(
            ResourceEndpoint.PERSON_UPDATE, data=person.update_dict()
        )

    async def update_person_face(self, person_id: str, face_data: str) -> None:
        """Update an existing person's face."""
        await self._async_request(
            ResourceEndpoint.PERSON_FACE_UPDATE,
            data={"personId": person_id, "faceData": face_data},
        )

    async def delete_person(self, person_id: str) -> None:
        """Delete a person."""
        await self._async_request(
            ResourceEndpoint.PERSON_DELETE,
            data={"personId": person_id},
        )
