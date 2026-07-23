import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.Clocks import ClockStartCondition
from PyMyGekko.resources.Clocks import ClockState


async def var_response(request):
    varResponseFile = open("tests/clocks/data/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/clocks/data/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_clocks(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        clocks = api.get_clocks()

        assert clocks is not None
        assert len(clocks) == 2

        assert clocks[0].entity_id == "item0"
        assert clocks[0].name == "Schiebetueren"
        assert clocks[0].state == ClockState.ON
        assert clocks[0].start_condition == ClockStartCondition.ON

        assert clocks[1].entity_id == "item1"
        assert clocks[1].name == "Tor Hofeinfahrt"
        assert clocks[1].state == ClockState.ON_COINCIDENCE
        assert clocks[1].start_condition == ClockStartCondition.OFF


@pytest.mark.asyncio
async def test_set_clock_state(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        clock = api.get_clocks()[0]

        written = {}

        async def fake_write(resource_path, value):
            written["resource_path"] = resource_path
            written["value"] = value

        api._data_provider.write_data = fake_write

        await clock.set_state(ClockState.ON_COINCIDENCE)
        assert written["resource_path"] == "/clocks/item0"
        assert written["value"] == "2"
