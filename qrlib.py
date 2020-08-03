import re
import asyncio

from aiohttp import ClientSession
from typing import (
    Any,
    Awaitable,
    Pattern,
    Tuple,
    Union,
    Callable,
    Dict,
)

Callback = Callable[..., Awaitable[Any]]


class Bot:
    def __init__(self, *, token: str, group_id: int, prefix: str = ""):
        self.token = token
        self.group_id = group_id
        self.prefix = prefix
        self.handlers: Dict[Pattern[str], Callback] = {}
        self.URL = "https://api.vk.com/method/"
        self.v = "5.110"
        self.base_params = {"group_id": group_id, "access_token": token, "v": self.v}

    def message_handler(
        self, *, text: Union[str, Pattern[str]] = re.compile(".*", re.IGNORECASE)
    ) -> Callable[..., Callback]:
        if isinstance(text, str):
            text_escaped: str = re.escape(self.prefix + text) + "$"
            text_pattern: Pattern[str] = re.compile(
                re.sub(r"<(\w+)>", r"(?P<\g<1>>\\w+)", text_escaped), re.IGNORECASE
            )
        elif self.prefix:
            text_pattern = re.compile(self.prefix + text.pattern, re.IGNORECASE)

        def wrapper(handler: Callback) -> Callback:
            self.handlers.update({text_pattern: handler})

            async def inner(*a: Tuple[Any], **kw: Dict[str, Any]) -> Any:
                return await handler(*a, **kw)

            return inner

        return wrapper

    async def __get(
        self, session: ClientSession, url: str, params: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        params.update(self.base_params)
        async with session.get(url, params=params) as response:
            assert response.status == 200
            return await response.json()

    async def __getLongPollServer(self, session: ClientSession):
        r = (await self.__get(session, self.URL + "groups.getLongPollServer"))[
            "response"
        ]
        return (r["key"], r["server"], r["ts"])

    async def __main(self) -> None:
        async with ClientSession() as session:
            key, server, ts = await self.__getLongPollServer(session)
            while True:
                r = await self.__get(
                    session,
                    server,
                    params={"act": "a_check", "key": key, "ts": ts, "wait": 25},
                )
                ts = r["ts"]
                if r["updates"]:
                    print(r["updates"])
                    text: str = r["updates"][0]["object"]["message"]["text"]
                    peer_id = r["updates"][0]["object"]["message"]["peer_id"]
                    for filter_, handler in self.handlers.items():
                        # match: Match[str]
                        if (match := filter_.match(text)) :
                            await self.__get(
                                session,
                                self.URL + "messages.send",
                                params={
                                    "peer_id": peer_id,
                                    "random_id": 0,
                                    "message": await handler(**match.groupdict()),
                                },
                            )
                            break

    def run(self):
        asyncio.run(self.__main())
