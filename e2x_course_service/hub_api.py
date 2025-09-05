import json

from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import url_path_join as ujoin
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse


class HubAPI:
    def __init__(self, hub: HubOAuth):
        self.hub = hub
        self.client = AsyncHTTPClient()

    @property
    def auth_header(self):
        return {"Authorization": f"token {self.hub.api_token}"}

    @property
    def hub_api_url(self):
        return self.hub.api_url

    async def request(self, url, method="GET", body=None) -> HTTPResponse:
        req = HTTPRequest(url, method=method, headers=self.auth_header, body=body)
        return await self.client.fetch(req)

    async def list_users(self):
        url = ujoin(self.hub_api_url, "users")
        resp: HTTPResponse = await self.request(url, method="GET")
        return resp.body

    async def create_user(self, username: str):
        url = ujoin(self.hub_api_url, "users", username)
        resp: HTTPResponse = await self.request(url, method="POST", body="{}")
        return resp.body

    async def create_users(self, usernames: list):
        url = ujoin(self.hub_api_url, "users")
        body = {
            "usernames": usernames,
            "admin": False,
        }
        resp: HTTPResponse = await self.request(url, method="POST", body=json.dumps(body))
        return resp.body

    async def get_group(self, groupname: str):
        url = ujoin(self.hub_api_url, "groups", groupname)
        resp: HTTPResponse = await self.request(url, method="GET")
        return resp.body
