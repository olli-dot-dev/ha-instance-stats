"""Config flow for HA Instance Stats."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL


class HAInstanceStatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Instance Stats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow one instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="HA Instance Stats",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "name": "HA Instance Stats",
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return HAInstanceStatsOptionsFlow()


class HAInstanceStatsOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
