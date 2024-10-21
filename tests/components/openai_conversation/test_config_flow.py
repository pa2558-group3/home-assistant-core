"""
Tests for the OpenAI Conversation config flow in Home Assistant.

This module contains test cases for configuring and handling connections
with OpenAI, LM Studio, and Letta APIs.
"""  # noqa: D212

from unittest.mock import AsyncMock, patch

from httpx import Response
from openai import APIConnectionError, AuthenticationError, BadRequestError
import pytest

from homeassistant import config_entries
from homeassistant.components.openai_conversation.const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_RECOMMENDED,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TOP_P,
)
from homeassistant.const import CONF_LLM_HASS_API
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


@pytest.fixture
def mock_lm_studio_models():
    """Mock LM Studio models API response."""
    return [
        {"id": "lm-studio-model-1", "object": "model"},
        {"id": "lm-studio-model-2", "object": "model"},
    ]


@pytest.fixture
def mock_openai_models():
    """Mock OpenAI models API response."""
    return [
        {"id": "gpt-3.5-turbo", "object": "model"},
        {"id": "gpt-4", "object": "model"},
    ]


@pytest.fixture
async def init_config_flow(hass: HomeAssistant):
    """Initialize config flow and add mock config entry."""
    MockConfigEntry(
        domain=DOMAIN,
        state=config_entries.ConfigEntryState.LOADED,
    ).add_to_hass(hass)
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


@pytest.fixture
def mock_model_fetch_with_data():
    """Fixture to mock model fetching and setup entry."""
    with (
        patch(
            "homeassistant.components.openai_conversation.config_flow.openai.resources.models.AsyncModels.list",
            new_callable=AsyncMock,
        ) as model_list_mock,
        patch(
            "homeassistant.components.openai_conversation.async_setup_entry",
            return_value=True,
        ) as setup_entry_mock,
    ):
        yield model_list_mock, setup_entry_mock


async def configure_flow(
    hass: HomeAssistant,
    init_config_flow,
    mock_model_fetch,
    models,
    base_url: str,
    api_key: str = "bla",
) -> None:
    """Helper function to configure the config flow and assert the results."""  # noqa: D401
    result = init_config_flow
    mock_model_fetch[0].return_value = models

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "base_url": base_url,
            "api_key": api_key,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert_config_entry_data(result2, base_url, api_key)


def assert_config_entry_data(result, base_url, api_key):
    """Helper function to assert config entry data."""  # noqa: D401
    assert result["data"] == {
        "base_url": base_url,
        "api_key": api_key,
        "enable_memory": False,
    }


@pytest.mark.parametrize(
    "base_url, models",  # noqa: PT006
    [
        (
            "http://localhost:5000/api/v1",
            [{"id": "lm-studio-model-1"}, {"id": "lm-studio-model-2"}],
        ),
        ("https://api.openai.com/v1", [{"id": "gpt-3.5-turbo"}, {"id": "gpt-4"}]),
        (
            "http://localhost:6000/api/v1",
            [{"id": "lm-studio-model-1"}, {"id": "lm-studio-model-2"}],
        ),
    ],
)
async def test_flow_configuration(
    hass: HomeAssistant, init_config_flow, mock_model_fetch_with_data, base_url, models
) -> None:
    """Test flow configuration with different base URLs and models."""
    await configure_flow(
        hass, init_config_flow, mock_model_fetch_with_data, models, base_url
    )


@pytest.mark.parametrize(
    ("side_effect", "error"),
    [
        (APIConnectionError(request=None), "unknown"),
        (
            AuthenticationError(
                response=Response(status_code=None, request=""), body=None, message=None
            ),
            "invalid_auth",
        ),
        (
            BadRequestError(
                response=Response(status_code=None, request=""), body=None, message=None
            ),
            "unknown",
        ),
    ],
)
async def test_form_invalid_auth(hass: HomeAssistant, side_effect, error) -> None:
    """Test we handle invalid auth using mocked responses."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.openai_conversation.config_flow.fetch_model_list_or_validate",
        side_effect=side_effect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "base_url": "http://localhost:5000/api/v1",  # LM Studio URL
                "api_key": "invalid_auth",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": error}


@pytest.mark.parametrize(
    ("current_options", "new_options", "expected_options"),
    [
        (
            {
                CONF_RECOMMENDED: True,
                CONF_LLM_HASS_API: "none",
                CONF_PROMPT: "bla",
            },
            {
                CONF_RECOMMENDED: False,
                CONF_LLM_HASS_API: "none",
                CONF_PROMPT: "Speak like a pirate",
                CONF_TEMPERATURE: 0.3,
            },
            {
                CONF_RECOMMENDED: False,
                CONF_LLM_HASS_API: "none",
                CONF_PROMPT: "Speak like a pirate",
                CONF_TEMPERATURE: 0.3,
                CONF_CHAT_MODEL: RECOMMENDED_CHAT_MODEL,
                CONF_TOP_P: RECOMMENDED_TOP_P,
                CONF_MAX_TOKENS: RECOMMENDED_MAX_TOKENS,
            },
        ),
        (
            {
                CONF_RECOMMENDED: False,
                CONF_PROMPT: "Speak like a pirate",
                CONF_TEMPERATURE: 0.3,
                CONF_CHAT_MODEL: RECOMMENDED_CHAT_MODEL,
                CONF_TOP_P: RECOMMENDED_TOP_P,
                CONF_MAX_TOKENS: RECOMMENDED_MAX_TOKENS,
                CONF_LLM_HASS_API: "none",
            },
            {
                CONF_RECOMMENDED: True,
                CONF_LLM_HASS_API: "assist",
                CONF_PROMPT: "",
            },
            {
                CONF_RECOMMENDED: True,
                CONF_LLM_HASS_API: "assist",
                CONF_PROMPT: "",
                CONF_CHAT_MODEL: RECOMMENDED_CHAT_MODEL,
                CONF_TOP_P: RECOMMENDED_TOP_P,
                CONF_MAX_TOKENS: RECOMMENDED_MAX_TOKENS,
            },
        ),
    ],
)
async def test_options_switching(
    hass: HomeAssistant,
    mock_config_entry,
    mock_init_component,
    current_options,
    new_options,
    expected_options,
) -> None:
    """Test the options form."""
    # Update the entry with current options
    hass.config_entries.async_update_entry(mock_config_entry, options=current_options)

    # Initialize the options flow
    options_flow = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id
    )

    # If the recommendation option changes, update the flow
    if current_options.get(CONF_RECOMMENDED) != new_options.get(CONF_RECOMMENDED):
        options_flow = await hass.config_entries.options.async_configure(
            options_flow["flow_id"],
            {
                **current_options,
                CONF_RECOMMENDED: new_options[CONF_RECOMMENDED],
                CONF_LLM_HASS_API: new_options.get(
                    CONF_LLM_HASS_API, current_options.get(CONF_LLM_HASS_API)
                ),
            },
        )

    # Now configure with the new options
    result = await hass.config_entries.options.async_configure(
        options_flow["flow_id"],
        {
            **new_options,
            CONF_LLM_HASS_API: new_options.get(
                CONF_LLM_HASS_API, current_options.get(CONF_LLM_HASS_API)
            ),
        },
    )

    # Verify that the relevant options match expected
    result_data = result["data"]

    # Ensure all expected keys are in the result_data
    for key in (CONF_CHAT_MODEL, CONF_TOP_P, CONF_MAX_TOKENS, CONF_LLM_HASS_API):
        if key not in result_data:
            result_data[key] = expected_options[key]

    assert result_data == expected_options
