import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.EMobils import EMobilChargeRequestState
from PyMyGekko.resources.EMobils import EMobilChargeState
from PyMyGekko.resources.EMobils import EMobilPluggedState


async def var_response(request):
    varResponseFile = open("tests/emobils/data/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/emobils/data/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_emobils(mock_server):
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
        emobils = api.get_emobils()

        assert emobils is not None
        assert len(emobils) == 1

        emobil = emobils[0]
        assert emobil.entity_id == "item0"
        assert emobil.name == "Slave 15"
        assert emobil.plugged_state == EMobilPluggedState.PLUGGED
        assert emobil.charge_state == EMobilChargeState.ON
        assert emobil.charge_request_state == EMobilChargeRequestState.ON
        assert emobil.current_charging_power == 11.00
        assert emobil.maximum_charging_power == 22.00
        assert emobil.charging_power_setpoint == 11.00
        assert emobil.electric_current_setpoint == 16
        assert emobil.charge_user_name == "Max Mustermann"
        assert emobil.charge_duration_time == "01:23:45"
        assert emobil.current_charging_energy == 5.40
        assert emobil.charge_start_time == "18:00:00"
        assert emobil.charge_user_index == 3


@pytest.mark.asyncio
async def test_emobil_commands(mock_server):
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
        emobil = api.get_emobils()[0]

        written = []

        async def fake_write(resource_path, value):
            written.append((resource_path, value))

        api._data_provider.write_data = fake_write

        await emobil.start_charge()
        await emobil.stop_charge()
        await emobil.set_charging_power_setpoint(7.5)

        assert written == [
            ("/emobils/item0", "1"),
            ("/emobils/item0", "-1"),
            ("/emobils/item0", "CS7.5"),
        ]
