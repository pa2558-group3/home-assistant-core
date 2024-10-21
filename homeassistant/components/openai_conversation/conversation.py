"""Conversation support for OpenAI."""

from collections.abc import Callable
from typing import Any, Literal

import openai
from openai._types import NOT_GIVEN
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition
from voluptuous_openapi import convert

from homeassistant.components import assist_pipeline, conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LLM_HASS_API, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, TemplateError
from homeassistant.helpers import device_registry as dr, intent, llm, template
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import ulid

from . import OpenAIConfigEntry
from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TOP_P,
)

# Max number of back and forth with the LLM to generate a response
MAX_TOOL_ITERATIONS = 10


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: OpenAIConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    agent = OpenAIConversationEntity(config_entry)
    async_add_entities([agent])


def _format_tool(
    tool: llm.Tool, custom_serializer: Callable[[Any], Any] | None
) -> ChatCompletionToolParam:
    """Format tool specification."""
    tool_spec = FunctionDefinition(
        name=tool.name,
        parameters=convert(tool.parameters, custom_serializer=custom_serializer),
    )
    if tool.description:
        tool_spec["description"] = tool.description
    return ChatCompletionToolParam(type="function", function=tool_spec)


class OpenAIConversationEntity(
    conversation.ConversationEntity, conversation.AbstractConversationAgent
):
    """OpenAI conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: OpenAIConfigEntry) -> None:
        """Initialize the agent."""
        self.entry = entry
        self.history: dict[str, list[ChatCompletionMessageParam]] = {}
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="OpenAI",
            model="ChatGPT",
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        if self.entry.options.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        assist_pipeline.async_migrate_engine(
            self.hass, "conversation", self.entry.entry_id, self.entity_id
        )
        conversation.async_set_agent(self.hass, self.entry, self)
        self.entry.async_on_unload(
            self.entry.add_update_listener(self._async_entry_update_listener)
        )

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        conversation_id, messages = self._initialize_conversation(user_input)
        intent_response = intent.IntentResponse(language=user_input.language)
        llm_api, tools = await self._setup_llm_api(user_input, intent_response)
        if llm_api is None:
            return self._create_conversation_result(intent_response, conversation_id)

        prompt = await self._generate_prompt(user_input, llm_api, intent_response)
        if prompt is None:
            return self._create_conversation_result(intent_response, conversation_id)

        return await self._generate_response(
            user_input, conversation_id, messages, prompt, tools, intent_response
        )

    def _initialize_conversation(self, user_input: conversation.ConversationInput):
        """Initialize conversation."""
        conversation_id = self._handle_invalid_conversation_id(user_input)
        messages = self.history.get(conversation_id, [])
        return conversation_id, messages

    def _handle_invalid_conversation_id(
        self, user_input: conversation.ConversationInput
    ):
        """Handle invalid conversation ID."""
        conversation_id = user_input.conversation_id or ""
        try:
            ulid.ulid_to_bytes(conversation_id)
            return ulid.ulid_now()
        except ValueError:
            return conversation_id

    async def _setup_llm_api(self, user_input, intent_response):
        """Setup LLM API and tools."""  # noqa: D401
        options = self.entry.options
        llm_api = None
        tools = None
        if options.get(CONF_LLM_HASS_API):
            try:
                llm_api = await llm.async_get_api(
                    self.hass,
                    options[CONF_LLM_HASS_API],
                    llm.LLMContext(
                        platform=DOMAIN,
                        context=user_input.context,
                        user_prompt=user_input.text,
                        language=user_input.language,
                        assistant=conversation.DOMAIN,
                        device_id=user_input.device_id,
                    ),
                )
                tools = [
                    _format_tool(tool, llm_api.custom_serializer)
                    for tool in llm_api.tools
                ]
            except HomeAssistantError as err:
                LOGGER.error("Error getting LLM API: %s", err)
                intent_response.async_set_error(
                    intent.IntentResponseErrorCode.UNKNOWN,
                    f"Error preparing LLM API: {err}",
                )
        return llm_api, tools

    def _create_conversation_result(self, intent_response, conversation_id):
        """Create a conversation result."""
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    async def _generate_prompt(self, user_input, llm_api, intent_response):
        """Generate the prompt for the LLM."""
        options = self.entry.options
        user_name = await self._get_user_name(user_input)
        try:
            prompt_parts = [
                await template.Template(
                    llm.BASE_PROMPT
                    + options.get(CONF_PROMPT, llm.DEFAULT_INSTRUCTIONS_PROMPT),
                    self.hass,
                ).async_render(
                    {
                        "ha_name": self.hass.config.location_name,
                        "user_name": user_name,
                        "llm_context": llm.LLMContext(
                            platform=DOMAIN,
                            context=user_input.context,
                            user_prompt=user_input.text,
                            language=user_input.language,
                            assistant=conversation.DOMAIN,
                            device_id=user_input.device_id,
                        ),
                    },
                    parse_result=False,
                )
            ]
            if llm_api:
                prompt_parts.append(llm_api.api_prompt)
                return "\n".join(prompt_parts)
        except TemplateError as err:
            LOGGER.error("Error rendering prompt: %s", err)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Sorry, I had a problem with my template: {err}",
            )
            return None

    async def _get_user_name(self, user_input):
        """Retrieve the user's name."""
        if user_input.context and user_input.context.user_id:
            user = await self.hass.auth.async_get_user(user_input.context.user_id)
            return user.name if user else None
        return None

    async def _generate_response(
        self, user_input, conversation_id, messages, prompt, tools, intent_response
    ):
        """Generate a response using the LLM."""
        client = self.entry.runtime_data
        for _iteration in range(MAX_TOOL_ITERATIONS):
            try:
                result = await client.chat.completions.create(
                    model=self.entry.options.get(
                        CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL
                    ),
                    messages=messages,
                    tools=tools or NOT_GIVEN,
                    max_tokens=self.entry.options.get(
                        CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS
                    ),
                    top_p=self.entry.options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
                    temperature=self.entry.options.get(
                        CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE
                    ),
                    user=conversation_id,
                )
                LOGGER.debug("Response %s", result)
                response = result.choices[0].message
                messages.append(response)
                self.history[conversation_id] = messages
                return self._create_conversation_result(
                    intent_response, conversation_id
                )
            except openai.OpenAIError as e:
                LOGGER.error("Error generating response: %s", e)
                intent_response.async_set_error(
                    intent.IntentResponseErrorCode.UNKNOWN,
                    "An error occurred while generating the response.",
                )
                return self._create_conversation_result(
                    intent_response, conversation_id
                )
        return None

    async def _async_entry_update_listener(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        # Reload as we update device info + entity name + supported features
        await hass.config_entries.async_reload(entry.entry_id)
