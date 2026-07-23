import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.EnergyManagers import EnergyManagerBatteryModel
from PyMyGekko.resources.EnergyManagers import EnergyManagerComponentState
from PyMyGekko.resources.EnergyManagers import EnergyManagerEmsEnabled
from PyMyGekko.resources.EnergyManagers import EnergyManagerState


async def var_response(request):
    varResponseFile = open("tests/energy_managers/data/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/energy_managers/data/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_energy_managers(mock_server):
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
        energy_managers = api.get_energy_managers()

        assert energy_managers is not None
        assert len(energy_managers) == 1

        energy_manager = energy_managers[0]
        assert energy_manager.entity_id == "item0"
        assert energy_manager.name == "Energy by MOBEX"

        assert energy_manager.grid_meter_state == EnergyManagerComponentState.ACTIVE
        assert energy_manager.solar_panel_state == EnergyManagerComponentState.ACTIVE
        assert energy_manager.battery_state == EnergyManagerComponentState.ACTIVE

        assert energy_manager.grid_meter_power == 825.00
        assert energy_manager.power_exported_to_grid == 0.00
        assert energy_manager.power_from_solar_panels == 363.00
        assert energy_manager.power_from_battery == 12.00
        assert energy_manager.power_charging_battery == 0.00
        assert energy_manager.home_power_consumption == 1200.00
        assert energy_manager.alternative_power_consumption == 363.00

        assert energy_manager.daily_energy_imported_from_grid == 11113.17
        assert energy_manager.daily_energy_exported_to_grid == 0.00
        assert energy_manager.daily_energy_from_solar_panels == 463.57
        assert energy_manager.daily_energy_from_battery == 132.91
        assert energy_manager.daily_energy_charging_battery == 0.00
        assert energy_manager.daily_home_energy_consumption == 11707.38

        assert energy_manager.load_shedding_state == EnergyManagerState.OFF
        assert energy_manager.ems_state == EnergyManagerState.OFF
        assert energy_manager.battery_model == EnergyManagerBatteryModel.E3DC_S10
        assert energy_manager.battery_soc == 42.0
        assert energy_manager.ems_enabled == EnergyManagerEmsEnabled.ENABLED

        assert energy_manager.max_power_consumption_from_grid == 3.00
        assert energy_manager.max_power_export_to_grid == 0.00
        assert energy_manager.max_power_solar_panels == 10000.00
        assert energy_manager.max_power_battery == 10000.00
