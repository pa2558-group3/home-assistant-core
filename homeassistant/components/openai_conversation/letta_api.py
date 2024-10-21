"""Following functions are only for Letta with LM Studio backend.

letta server --host 192.168.50.136 --port 8283 --debug.
"""

import logging

from requests import Response, get, request

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DEFAULT_LETTA_URL = "http://localhost:8283"
DEFAULT_TIMEOUT = 6.0


def _get_request(url: str, headers: dict | None, timeout: float | None) -> Response:
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    return get(url, headers=headers, timeout=timeout)


def _post_request(
    url: str, headers: dict | None, payload: dict | None, timeout: float | None
) -> Response:
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    return request("POST", url, json=payload, headers=headers, timeout=timeout)


def _check_lm_studio_backend():
    pass


async def list_LLM_backends(
    hass: HomeAssistant,
    base_url: str | None,
    headers: dict | None,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> Response:
    """Retrieve all available model ids."""
    if base_url is None:
        base_url = DEFAULT_LETTA_URL
    API = "/v1/models/"
    return await hass.async_add_executor_job(
        _get_request, base_url + API, headers, timeout
    )


async def list_agents(
    hass: HomeAssistant,
    base_url: str | None,
    user_id: str | None,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> Response:
    """List all agents associated with a given user."""
    if base_url is None:
        base_url = DEFAULT_LETTA_URL
    API = "/v1/agents/"
    headers = {
        "user_id": user_id,
        "Authorization": "Bearer <token>",
    }
    return await hass.async_add_executor_job(
        _get_request, base_url + API, headers, timeout
    )


async def send_message(
    hass: HomeAssistant,
    base_url: str | None,
    user_id: str | None,
    agent_id: str | None,
    data: dict | None,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> Response:
    """Process a user message and return the agent's response."""
    if base_url is None:
        base_url = DEFAULT_LETTA_URL
    API = f"/v1/agents/{agent_id}/messages"
    headers = {
        "user_id": user_id,
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json",
    }
    return await hass.async_add_executor_job(
        _post_request, base_url + API, headers, data, timeout
    )
