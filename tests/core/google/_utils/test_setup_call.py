"""Tests the `google._utils.setup_call` module."""

from unittest.mock import MagicMock, patch

import pytest
from google.genai.types import (
    FunctionCallingConfig,
    FunctionCallingConfigMode,
    GenerateContentConfig,
)
from pydantic import BaseModel

from mirascope.core.google._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.google._utils._setup_call import setup_call
from mirascope.core.google.tool import GoogleTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_utils.setup_call = mock_base_setup_call
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "contents" in call_kwargs and call_kwargs["contents"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, GoogleTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    mock_client_class.assert_called_once_with()
    assert create(**call_kwargs)
    mock_client.models.generate_content.assert_called_once_with(**call_kwargs)
    mock_client.models.generate_content.reset_mock()
    assert create(stream=True, **call_kwargs)
    mock_client.models.generate_content_stream.assert_called_once_with(**call_kwargs)
    mock_client.models.generate_content_stream.reset_mock()
    assert create(stream=False, **call_kwargs)
    mock_client.models.generate_content.assert_called_once_with(**call_kwargs)


@pytest.mark.parametrize(
    "generation_config_type",
    [dict, GenerateContentConfig],
)
@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    generation_config_type: type,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "parts": [{"type": "text", "text": "test"}]}
    ]
    tools = [MagicMock()]
    mock_base_setup_call.return_value[-1]["tools"] = tools
    mock_base_setup_call.return_value[-1]["config"] = generation_config_type(
        candidate_count=1,
        max_output_tokens=100,
        response_mime_type="application/xml",
        response_schema=None,
        stop_sequences=["\n"],
        temperature=0.5,
        top_k=0,
        top_p=0,
    )
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        response_model=None,
        stream=False,
    )
    mock_client_class.assert_called_once_with()
    assert isinstance(messages[-1], dict)
    assert "parts" in messages[-1]
    assert isinstance(messages[-1]["parts"], list)
    assert messages[-1]["parts"][-1] == {
        "text": mock_utils.json_mode_content.return_value
    }
    assert "config" in call_kwargs
    assert call_kwargs["config"] == GenerateContentConfig(
        system_instruction=None,
        temperature=0.5,
        top_p=0.0,
        top_k=0.0,
        candidate_count=1,
        max_output_tokens=100,
        stop_sequences=["\n"],
        response_logprobs=None,
        logprobs=None,
        presence_penalty=None,
        frequency_penalty=None,
        seed=None,
        response_mime_type="application/json",
        response_schema=None,
        routing_config=None,
        safety_settings=None,
        tools=tools,  # pyright: ignore [reportArgumentType]
        tool_config=None,
        cached_content=None,
        response_modalities=None,
        media_resolution=None,
        speech_config=None,
        audio_timestamp=None,
        automatic_function_calling=None,
        thinking_config=None,
    )


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_extract(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""
    mock_tool = MagicMock()
    mock_tool._name.side_effect = lambda: "test"
    mock_base_setup_call.return_value[2] = [mock_tool]
    mock_utils.setup_call = mock_base_setup_call
    _, _, _, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=BaseModel,
        stream=False,
    )
    mock_client_class.assert_called_once_with()
    assert "config" in call_kwargs and isinstance(
        call_kwargs["config"], GenerateContentConfig
    )
    config = call_kwargs["config"]
    assert config.tool_config is not None
    assert config.tool_config.function_calling_config is not None
    assert config.tool_config.function_calling_config == FunctionCallingConfig(
        mode=FunctionCallingConfigMode.ANY, allowed_function_names=["test"]
    )
