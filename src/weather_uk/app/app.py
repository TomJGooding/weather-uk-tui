from textual.app import App

from weather_uk import config
from weather_uk.app.screens.forecast import ForecastScreen
from weather_uk.app.screens.locations import LocationsScreen
from weather_uk.app.screens.welcome import WelcomeScreen
from weather_uk.domain.weather_api_client import (
    AbstractWeatherAPIClient,
    MetOfficeAPIClient,
)


class WeatherUkApp(App):
    CSS_PATH = "weather-uk.css"
    SCREENS = {
        "welcome": WelcomeScreen,
        "locations": LocationsScreen,
        "forecast": ForecastScreen,
    }
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        self._user_config: config.UserConfig = config.load_config()
        self._weather_api: AbstractWeatherAPIClient = MetOfficeAPIClient()
        self._location_id: int | None = None

        if not self._user_config.api_key:
            self.push_screen("welcome")
        else:
            self._weather_api.api_key = self._user_config.api_key
            self.push_screen("locations")


def run() -> None:
    app = WeatherUkApp()
    app.run()
