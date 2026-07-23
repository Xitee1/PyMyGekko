import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.HeatingCircuits import HeatingCircuitCoolingModeState
from PyMyGekko.resources.HeatingCircuits import HeatingCircuitDeviceModel
from PyMyGekko.resources.HeatingCircuits import HeatingCircuitState


async def var_response(request):
    varResponseFile = open("tests/heating_circuits/data/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/heating_circuits/data/api_var_status_response.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_heating_circuits(mock_server):
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
        heating_circuits = api.get_heating_circuits()

        assert heating_circuits is not None
        assert len(heating_circuits) == 1

        heating_circuit = heating_circuits[0]
        assert heating_circuit.entity_id == "item0"
        assert heating_circuit.name == "Heizen/Kuehlen"
        assert heating_circuit.device_model == HeatingCircuitDeviceModel.BUDERUS
        assert heating_circuit.flow_temperature == 35.00
        assert heating_circuit.return_flow_temperature == 28.00
        assert heating_circuit.dew_point == 12.00
        assert heating_circuit.pump_working_level == 80.00
        assert heating_circuit.cooling_mode_state == HeatingCircuitCoolingModeState.OFF
        assert heating_circuit.flow_temperature_setpoint == 40.00
        assert heating_circuit.valve_opening_level == 100.00
        assert heating_circuit.state == HeatingCircuitState.AUTO
