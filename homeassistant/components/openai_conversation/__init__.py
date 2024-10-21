"""The OpenAI Conversation integration."""

from __future__ import annotations

import openai
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_ENABLE_MEMORY,
    Platform,
)
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import (
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, LOGGER, RECOMMENDED_BASE_URL

SERVICE_GENERATE_IMAGE = "generate_image"
PLATFORMS = (Platform.CONVERSATION,)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type OpenAIConfigEntry = ConfigEntry[openai.AsyncClient]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up OpenAI Conversation."""

    async def render_image(call: ServiceCall) -> ServiceResponse:
        """Render an image with dall-e."""
        entry_id = call.data["config_entry"]
        entry = hass.config_entries.async_get_entry(entry_id)

        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_config_entry",
                translation_placeholders={"config_entry": entry_id},
            )

        client: openai.AsyncClient = entry.runtime_data

        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=call.data["prompt"],
                size=call.data["size"],
                quality=call.data["quality"],
                style=call.data["style"],
                response_format="url",
                n=1,
            )
        except openai.OpenAIError as err:
            raise HomeAssistantError(f"Error generating image: {err}") from err

        return response.data[0].model_dump(exclude={"b64_json"})

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_IMAGE,
        render_image,
        schema=vol.Schema(
            {
                vol.Required("config_entry"): selector.ConfigEntrySelector(
                    {
                        "integration": DOMAIN,
                    }
                ),
                vol.Required("prompt"): cv.string,
                vol.Optional("size", default="1024x1024"): vol.In(
                    ("1024x1024", "1024x1792", "1792x1024")
                ),
                vol.Optional("quality", default="standard"): vol.In(("standard", "hd")),
                vol.Optional("style", default="vivid"): vol.In(("vivid", "natural")),
            }
        ),
        supports_response=SupportsResponse.ONLY,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: OpenAIConfigEntry) -> bool:
    """Set up OpenAI Conversation from a config entry."""
    LOGGER.info("__init__")
    LOGGER.info(entry.as_dict())
    timeout_duration = 10.0
    try:
        base_url = entry.options[CONF_BASE_URL]

        # if the base_url is not the recommended, which means it needs to be checked if is up.
        # new function to do this
        if base_url != RECOMMENDED_BASE_URL:
            timeout_duration = 6.0
    except KeyError:
        base_url = entry.data[CONF_BASE_URL]

    # check CONF_ENABLE_MEMORY
    if entry.data.get(CONF_ENABLE_MEMORY):
        # if enabled, only for letta with LM Studio Backend
        from .letta_api import list_LLM_backends  # pylint: disable=import-outside-toplevel  # noqa: I001

        try:
            async_result = await list_LLM_backends(
                hass, base_url=base_url, headers={"Authorization": "Bearer token"}
            )  # headers is unnecessary
            if async_result.status_code != 200:
                # import json  # pylint: disable=import-outside-toplevel  # noqa: I001

                # response_json = json.loads(async_result.text)[0]

                # LOGGER.info(f"response_json:{response_json}")  # noqa: G004
                async_result.raise_for_status()
                from requests import exceptions
        except ConnectionRefusedError as err:
            raise ConfigEntryNotReady(err) from err
        except exceptions.HTTPError as err:
            raise ConfigEntryNotReady(err) from err

    else:
        # if not enabled(default setup)
        client = openai.AsyncOpenAI(base_url=base_url, api_key=entry.data[CONF_API_KEY])

        try:
            async_pages = await hass.async_add_executor_job(
                client.with_options(timeout=timeout_duration).models.list
            )
            [model.id async for model in async_pages]
        except openai.AuthenticationError as err:
            LOGGER.error("Invalid API key: %s", err)
            return False
        except openai.OpenAIError as err:
            raise ConfigEntryNotReady(err) from err

        entry.runtime_data = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenAI."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
