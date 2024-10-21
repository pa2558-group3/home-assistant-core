"""Tests for conversation.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import openai
import pytest

from homeassistant.components.openai_conversation import OpenAIConfigEntry
from homeassistant.components.openai_conversation.conversation import (
    OpenAIConversationEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

# Mock constants
DOMAIN = "openai_conversation"
CONF_LLM_HASS_API = "llm_hass_api"


@pytest.fixture
def mock_entry():
    """Create a mock OpenAIConfigEntry."""
    entry = MagicMock(spec=OpenAIConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.title = "Test Entry"
    entry.options = {CONF_LLM_HASS_API: "test_api"}
    entry.runtime_data = MagicMock()  # Mock the runtime_data attribute
    return entry


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.auth = MagicMock()  # Mock the auth attribute
    hass.auth.async_get_user = AsyncMock(
        return_value=None
    )  # Mock the async_get_user method
    hass.config = MagicMock()  # Mock the config attribute
    hass.config.location_name = "Test Location"  # Set a mock location name
    hass.data = MagicMock()  # Mock the data attribute
    return hass


@pytest.fixture
def mock_intent_response():
    """Create a mock IntentResponse."""
    return MagicMock(spec=intent.IntentResponse)


@pytest.fixture
def openai_conversation_entity(mock_entry, mock_hass):
    """Create an instance of OpenAIConversationEntity with a mocked hass."""
    entity = OpenAIConversationEntity(mock_entry)
    entity.hass = mock_hass  # Set the hass attribute
    return entity


def test_initialize_conversation(openai_conversation_entity):
    """Test the _initialize_conversation method."""
    user_input = MagicMock()
    user_input.conversation_id = "valid_id"
    conversation_id, messages = openai_conversation_entity._initialize_conversation(
        user_input
    )
    assert conversation_id == "valid_id"
    assert messages == []


@pytest.mark.asyncio
async def test_setup_llm_api(openai_conversation_entity, mock_intent_response):
    """Test the _setup_llm_api method."""
    user_input = MagicMock()
    with patch(
        "homeassistant.helpers.llm.async_get_api", new_callable=AsyncMock
    ) as mock_get_api:
        mock_get_api.return_value = MagicMock()
        llm_api, tools = await openai_conversation_entity._setup_llm_api(
            user_input, mock_intent_response
        )
        assert llm_api is not None
        assert tools is not None


@pytest.mark.asyncio
async def test_generate_prompt(openai_conversation_entity, mock_intent_response):
    """Test the _generate_prompt method."""
    user_input = MagicMock()
    llm_api = MagicMock()
    llm_api.api_prompt = "API prompt"  # Ensure this is a string

    # Mock the template rendering
    with patch(
        "homeassistant.helpers.template.Template.async_render", new_callable=AsyncMock
    ) as mock_render:
        mock_render.return_value = "Rendered prompt"

        prompt = await openai_conversation_entity._generate_prompt(
            user_input, llm_api, mock_intent_response
        )
        assert prompt is not None
        assert "Rendered prompt" in prompt
        assert "API prompt" in prompt


@pytest.mark.asyncio
async def test_generate_response(openai_conversation_entity, mock_intent_response):
    """Test the _generate_response method."""
    user_input = MagicMock()
    conversation_id = "test_id"
    messages = []
    prompt = "Test prompt"
    tools = None
    # Mock the runtime_data and its methods
    openai_conversation_entity.entry.runtime_data = MagicMock()
    openai_conversation_entity.entry.runtime_data.chat.completions.create = AsyncMock(
        side_effect=openai.OpenAIError("Test error")
    )
    result = await openai_conversation_entity._generate_response(
        user_input, conversation_id, messages, prompt, tools, mock_intent_response
    )
    assert result is not None
