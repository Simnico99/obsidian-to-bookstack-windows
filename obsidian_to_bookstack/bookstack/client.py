import json
import os
from abc import ABC, abstractmethod

import urllib3

from .constants import *


class Client(ABC):
    ...


class RemoteClient(Client):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.id = os.getenv("BOOKSTACK_TOKEN_ID")
        self.secret = os.getenv("BOOKSTACK_TOKEN_SECRET")
        self.base_url = os.getenv("BOOKSTACK_BASE_URL")
        self.headers = {"Authorization": f"Token {self.id}:{self.secret}"}
        self.http = urllib3.PoolManager()

    def _make_request(
        self,
        request_type: RequestType,
        endpoint: BookstackAPIEndpoints | DetailedBookstackLink,
        body=None,
        json=None,
    ) -> urllib3.BaseHTTPResponse:
        """Make a HTTP request to a Bookstack API Endpoint"""

        assert self.base_url

        request_url = self.base_url + endpoint.value
        resp = self.http.request(
            request_type.value, request_url, headers=self.headers, body=body, json=json
        )
        
        # Check for HTTP errors
        if resp.status >= 400:
            error_data = {}
            try:
                error_data = json.loads(resp.data.decode())
            except:
                error_data = {"message": resp.data.decode() if resp.data else "Unknown error"}
            
            error_msg = error_data.get("message", error_data.get("error", f"HTTP {resp.status}"))
            raise Exception(f"API request failed: {error_msg} (Status: {resp.status}, URL: {request_url})")
        
        return resp

    def _get_from_client(self, endpoint: BookstackAPIEndpoints):
        """Make a GET request to a Bookstack API Endpoint"""
        resp = self._make_request(RequestType.GET, endpoint)
        assert resp

        try:
            # Decode response with proper encoding handling for Windows
            response_text = resp.data.decode('utf-8')
            data = json.loads(response_text)
        except UnicodeDecodeError as e:
            raise Exception(f"Failed to decode API response: {e}\nResponse (first 200 chars): {resp.data[:200]}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response as JSON: {e}\nResponse: {response_text[:500]}")
        
        # Check if response has expected structure
        if "data" not in data:
            # Some endpoints might return data directly, not wrapped in "data"
            if isinstance(data, list):
                return data
            # If it's an error response, raise an exception
            if "error" in data or "message" in data:
                error_msg = data.get("message", data.get("error", "Unknown API error"))
                raise Exception(f"API error: {error_msg}\nFull response: {data}")
            # Log the unexpected response structure for debugging
            raise Exception(
                f"Unexpected API response structure. Expected 'data' key but got: {list(data.keys())}\n"
                f"Full response: {data}\n"
                f"This might indicate:\n"
                f"  1. Invalid API credentials (check BOOKSTACK_TOKEN_ID and BOOKSTACK_TOKEN_SECRET)\n"
                f"  2. Incorrect BOOKSTACK_BASE_URL\n"
                f"  3. API endpoint format has changed"
            )
        
        return data["data"]


class LocalClient(Client):
    ...
