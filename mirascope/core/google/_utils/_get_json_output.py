"""Get JSON output from a Google response."""

import json

from proto.marshal.collections import RepeatedComposite

from ..call_response import GoogleCallResponse
from ..call_response_chunk import GoogleCallResponseChunk


def get_json_output(
    response: GoogleCallResponse | GoogleCallResponseChunk, json_mode: bool
) -> str:
    """Extracts the JSON output from a Google response."""
    if isinstance(response, GoogleCallResponse):
        if json_mode and (content := response.content):
            json_start = content.index("{")
            json_end = content.rfind("}")
            return content[json_start : json_end + 1]
        elif tool_calls := [
            part.function_call
            for part in response.response.parts
            if part.function_call.args
        ]:
            return json.dumps(
                {
                    k: v if not isinstance(v, RepeatedComposite) else list(v)
                    for k, v in tool_calls[0].args.items()
                }
            )
        else:
            raise ValueError("No tool call or JSON object found in response.")
    elif not json_mode:
        raise ValueError("Google only supports structured streaming in json mode.")
    return response.content
