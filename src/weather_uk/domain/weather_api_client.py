import json
from abc import ABC, abstractmethod
from typing import Optional

import requests

from weather_uk.data import models
from weather_uk.domain import serialisers


class AbstractWeatherAPIClient(ABC):
    @abstractmethod
    def check_authentication(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_locations_list(self) -> list[models.Location]:
        raise NotImplementedError

    @abstractmethod
    def get_forecast(self, location_id: int) -> list[models.ForecastDay]:
        raise NotImplementedError


class MetOfficeAPIClient(AbstractWeatherAPIClient):
    BASE_URL: str = "http://datapoint.metoffice.gov.uk/public/data/"
    DATATYPE: str = "json"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key: str | None = api_key
        self._session: requests.Session = requests.Session()

    def check_authentication(self) -> None:
        # Try a small request (0.1kB) - if no exceptions then all is well!
        resource: str = "txt/wxfcs/regionalforecast/json/capabilities"
        self._request(resource)

    def get_locations_list(self) -> list[models.Location]:
        resource: str = f"val/wxfcs/all/{self.DATATYPE}/sitelist"
        resp: requests.Response = self._request(resource)
        json_data: dict = json.loads(
            resp.text,
            cls=serialisers.NumbersStoredAsTextDecoder,
        )

        return serialisers.decode_met_office_locations(json_data)

    def get_forecast(self, location_id: int) -> list[models.ForecastDay]:
        resource: str = f"val/wxfcs/all/{self.DATATYPE}/{location_id}"
        query: str = "res=3hourly&"
        resp: requests.Response = self._request(resource, query)
        json_data = json.loads(
            resp.text,
            cls=serialisers.NumbersStoredAsTextDecoder,
        )

        return serialisers.decode_met_office_forecast(json_data)

    def _request(
        self,
        resource: str,
        query: Optional[str] = None,
    ) -> requests.Response:
        req: requests.Request = self._build_request(resource, query)
        prepped: requests.PreparedRequest = req.prepare()
        try:
            resp: requests.Response = self._session.send(prepped)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            raise http_err
        except requests.exceptions.ConnectionError as cxn_err:
            raise cxn_err
        except requests.exceptions.Timeout as timeout_err:
            raise timeout_err
        except requests.exceptions.RequestException as req_err:
            raise req_err

        return resp

    def _build_request(
        self, resource: str, query: Optional[str] = None
    ) -> requests.Request:
        query = "" if not query else query
        url: str = f"{self.BASE_URL}{resource}?{query}key={self.api_key}"
        return requests.Request(method="GET", url=url)
