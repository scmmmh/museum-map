import logging
import math
import re
from datetime import datetime, timezone
from importlib.abc import Traversable
from mimetypes import guess_type

from meilisearch_python_async import Client
from sqlalchemy import func, select
from sqlalchemy.orm import noload, selectinload
from tornado import web

from museum_map.__about__ import __version__
from museum_map.models import Floor, FloorTopic, Group, Item, Room, create_sessionmaker

logger = logging.getLogger(__name__)


def setup_query(types, multi_load):
    query = None
    class_ = None
    if multi_load:
        multi_loader = selectinload
    else:
        multi_loader = noload
    if types == "rooms":
        query = select(Room).options(selectinload(Room.floor), multi_loader(Room.items), selectinload(Room.sample))
        class_ = Room
    elif types == "floors":
        query = select(Floor).options(
            multi_loader(Floor.rooms), multi_loader(Floor.samples), multi_loader(Floor.topics)
        )
        class_ = Floor
    elif types == "items":
        query = select(Item).options(selectinload(Item.room))
        class_ = Item
    elif types == "floor-topics":
        query = select(FloorTopic).options(selectinload(FloorTopic.group), selectinload(FloorTopic.floor))
        class_ = FloorTopic
    elif types == "groups":
        query = select(Group)
        class_ = Group
    return (query, class_)


class APIStatusHandler(web.RequestHandler):
    async def get(self):
        async with create_sessionmaker(self.application.settings["config"])():
            ready = False

        self.write({"version": __version__, "ready": ready})


class RequestBase(web.RequestHandler):
    def setup_query(self, types):
        return setup_query(types, not self.get_argument("relationships", "true").lower() == "false")


class APICollectionHandler(RequestBase):
    async def get(self, types):
        async with create_sessionmaker(self.application.settings["config"])() as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                for key, values in self.request.arguments.items():
                    if key.startswith("filter["):
                        column = key[key.find("[") + 1 : key.find("]")]
                        if values == "":
                            query = query.filter(getattr(class_, column).in_([]))
                        else:
                            for value in values:
                                value = value.decode()  # noqa: PLW2901
                                if value == "":
                                    query = query.filter(getattr(class_, column).in_([]))
                                else:
                                    split_values = [int(v) for v in value.split(",")]
                                    if len(split_values) == 1:
                                        query = query.filter(getattr(class_, column) == split_values[0])
                                    else:
                                        query = query.filter(getattr(class_, column).in_(split_values))
                result = await session.execute(query)
                items = [item.as_jsonapi() for item in result.unique().scalars()]
                self.write({"data": items})
            else:
                self.send_error(status_code=404)


class APIItemHandler(RequestBase):
    async def get(self, types, identifier):
        async with create_sessionmaker(self.application.settings["config"])() as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                query = query.filter(class_.id == int(identifier))
                item = (await session.execute(query)).scalars().first()
                if item is not None:
                    self.write({"data": item.as_jsonapi()})
                else:
                    self.send_error(status_code=404)
            else:
                self.send_error(status_code=404)


class APIConfigHandler(web.RequestHandler):
    def initialize(self, config: dict) -> None:
        self._config = config

    async def get(self):
        attributes = {
            "intro": self._config["app"]["intro"],
            "item": self._config["app"]["item"],
        }
        if "footer" in self._config["app"]:
            for footer_location in ["center", "right"]:
                if footer_location in self._config["app"]["footer"]:
                    if "footer" not in attributes:
                        attributes["footer"] = {}
                    attributes["footer"][footer_location] = {
                        "label": self._config["app"]["footer"][footer_location]["label"]
                    }
                    if "url" in self._config["app"]["footer"][footer_location]:
                        attributes["footer"][footer_location]["url"] = self._config["app"]["footer"][footer_location][
                            "url"
                        ]
        self.write({"data": {"id": "all", "type": "configs", "attributes": attributes}})


class APIPickHandler(RequestBase):
    async def get(self, pick_type):
        if pick_type in ["random", "todays"]:
            async with create_sessionmaker(self.application.settings["config"])() as session:
                query, class_ = self.setup_query("items")
                if query is not None and class_ is not None:
                    if pick_type == "random":
                        query = query.order_by(func.random()).limit(12)
                    elif pick_type == "todays":
                        total = (await session.execute(select(func.count()).select_from(class_))).scalars().first()
                        row_nr = (math.floor(datetime.now(tz=timezone.utc).timestamp() / 86400) % total) + 1
                        query = query.order_by(class_.id).offset(row_nr).limit(1)
                    result = await session.execute(query)
                    items = [item.as_jsonapi() for item in result.scalars()]
                    self.write({"data": items})
                else:
                    self.send_error(status_code=404)
        else:
            self.send_error(status_code=404)


class APISearchHandler(RequestBase):
    def initialize(self: "APISearchHandler"):
        self._client = Client(
            self.application.settings["config"]["search"]["url"], self.application.settings["config"]["search"]["key"]
        )
        self._index = None

    async def get(self: "APISearchHandler"):
        if self._index is None:
            self._index = await self._client.get_index("items")
        result = await self._index.search(
            self.get_argument("q"),
            limit=150,
            facets=["mmap_room", "mmap_floor"],
            filter=[f'mmap_room = {self.get_argument("room")}']
            if self.get_argument("room", default=None) is not None
            else [],
        )
        self.write(
            {
                "hits": result.hits,
                "facetDistribution": result.facet_distribution,
            }
        )


class FrontendHandler(web.RedirectHandler):
    """Handler for the frontend application files."""

    def initialize(self: "FrontendHandler", base: Traversable, html_injectors: dict | None = None) -> None:
        """Initialise the frontend handler."""
        self._base = base
        if html_injectors:
            self._html_injectors = html_injectors
        else:
            self._html_injectors = {}

    async def get(self: "FrontendHandler", path: str) -> None:
        """Get the file at the given path.

        :param path: The path to get.
        :type: path: str
        """
        self.xsrf_token  # noqa: B018
        if not path.strip():
            path = "/"
        try:
            logger.debug(f"Attempting to send {path}")
            await self._get_resource(self._base, path.split("/"))
        except FileNotFoundError:
            logger.debug("Sending index.html")
            await self._get_resource(self._base, ("index.html",), orig_path=path)

    async def _get_resource(
        self: "FrontendHandler", resource: Traversable, path: list[str], orig_path: str | None = None
    ) -> None:
        """Send a file.

        Performs mimetype guessing and sets the appropriate Content-Type header.

        :param resource: The root resource to serve files from
        :type resource: importlib.Traversable
        :param path: The path to the file to send
        :type path: list[str]
        :param orig_path: The original path, if this is sending the default index.html
        :type orig_path: str
        """
        for part in path:
            resource = resource / part
        try:
            data = resource.read_bytes()
            if orig_path:
                for key, injector in self._html_injectors.items():
                    match = re.match(key, orig_path)
                    if match:
                        html = data.decode("utf-8")
                        split_idx = html.find("</head>")
                        html = f"{html[:split_idx]}{await injector(*match.groups())}{html[split_idx:]}"
                        data = html.encode("utf-8")
            mimetype = guess_type(path[-1])
            if mimetype and mimetype[0]:
                self.set_header("Content-Type", mimetype[0])
            self.write(data)
        except IsADirectoryError as err:
            raise FileNotFoundError() from err


def create_inject_item_html(config):
    """Inject Twitter card meta tags."""

    async def inject_item_html(room_id: str, joke_id: str) -> str:
        try:
            async with create_sessionmaker(config)() as session:
                query, class_ = setup_query("items", False)
                query = query.filter(class_.id == int(joke_id))
                item = (await session.execute(query)).scalar()
                if item:
                    return f"""<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:site" content="@Hallicek"/>
<meta name="twitter:title" content="{item.attributes['title']}"/>
<meta name="twitter:image" content="{config['app']['base_url']}/images/{'/'.join(item.attributes['images'][0])}.jpg"/>
<meta name="twitter:image:alt" content="Image showing {item.attributes['title']}"/>
<meta property="og:url" content="{config['app']['base_url']}/room/{room_id}/{joke_id}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{item.attributes['title']}" />
<meta property="og:image" content="{config['app']['base_url']}/images/{'/'.join(item.attributes['images'][0])}.jpg" />
<meta name="og:image:alt" content="Image showing {item.attributes['title']}"/>"""
        except Exception:  # noqa: S110
            pass
        return ""

    return inject_item_html
