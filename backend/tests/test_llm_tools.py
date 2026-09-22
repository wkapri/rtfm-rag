"""complete_with_tools() request/response translation for each provider — the
risky part of tool-calling support, since each API represents a "tool result"
and "tool call arguments" differently (see each provider's complete_with_tools
for the specifics: Ollama's arguments arrive pre-parsed, OpenAI's as a JSON
string, Anthropic has no "tool" role at all). No real network calls — each
provider's httpx.Client.post is monkeypatched to return a canned httpx.Response
built from a real API's documented response shape.
"""

import httpx

from ragapp.llm.base import Message, ToolCall, ToolSpec
from ragapp.llm.providers.anthropic import AnthropicProvider
from ragapp.llm.providers.ollama import OllamaProvider
from ragapp.llm.providers.openai_compat import OpenAICompatProvider

_TOOLS = [ToolSpec(name="get_weather", description="Get the weather", input_schema={"type": "object"})]


def _response(status_code: int, json_body: dict) -> httpx.Response:
    # raise_for_status() needs a request attached, which a bare httpx.Response
    # built by hand doesn't have — attach a dummy one.
    return httpx.Response(status_code, json=json_body, request=httpx.Request("POST", "http://test"))


def _fake_post(response: httpx.Response):
    def post(url, json):
        return response

    return post


class TestOllama:
    def test_parses_tool_call(self, monkeypatch):
        provider = OllamaProvider()
        monkeypatch.setattr(
            provider._client,
            "post",
            _fake_post(
                _response(
                    200,
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {"function": {"name": "get_weather", "arguments": {"city": "Boston"}}}
                            ],
                        }
                    },
                )
            ),
        )

        turn = provider.complete_with_tools([{"role": "user", "content": "weather?"}], _TOOLS, "system")

        assert len(turn.tool_calls) == 1
        assert turn.tool_calls[0].name == "get_weather"
        assert turn.tool_calls[0].arguments == {"city": "Boston"}

    def test_parses_plain_text_response(self, monkeypatch):
        provider = OllamaProvider()
        monkeypatch.setattr(
            provider._client,
            "post",
            _fake_post(_response(200, {"message": {"role": "assistant", "content": "Hello!"}})),
        )

        turn = provider.complete_with_tools([{"role": "user", "content": "hi"}], _TOOLS, "system")

        assert turn.tool_calls == []
        assert turn.text == "Hello!"

    def test_replays_prior_tool_call_and_result(self, monkeypatch):
        provider = OllamaProvider()
        captured = {}

        def post(url, json):
            captured["payload"] = json
            return _response(200, {"message": {"role": "assistant", "content": "done"}})

        monkeypatch.setattr(provider._client, "post", post)

        messages: list[Message] = [
            {"role": "user", "content": "weather?"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [ToolCall(id="1", name="get_weather", arguments={"city": "Boston"})],
            },
            {"role": "tool", "tool_call_id": "1", "content": "Sunny, 70F"},
        ]
        provider.complete_with_tools(messages, _TOOLS, "system")

        sent = captured["payload"]["messages"]
        assert sent[2]["tool_calls"][0]["function"]["name"] == "get_weather"
        assert sent[3] == {"role": "tool", "content": "Sunny, 70F"}


class TestAnthropic:
    def test_parses_tool_use_block(self, monkeypatch):
        provider = AnthropicProvider(api_key="sk-test", model="claude-test")
        monkeypatch.setattr(
            provider._client,
            "post",
            _fake_post(
                _response(
                    200,
                    {
                        "content": [
                            {"type": "tool_use", "id": "toolu_1", "name": "get_weather", "input": {"city": "Boston"}}
                        ]
                    },
                )
            ),
        )

        turn = provider.complete_with_tools([{"role": "user", "content": "weather?"}], _TOOLS, "system")

        assert turn.tool_calls == [ToolCall(id="toolu_1", name="get_weather", arguments={"city": "Boston"})]
        assert turn.text is None

    def test_tool_result_becomes_user_turn(self, monkeypatch):
        provider = AnthropicProvider(api_key="sk-test", model="claude-test")
        captured = {}

        def post(url, json):
            captured["payload"] = json
            return _response(200, {"content": [{"type": "text", "text": "done"}]})

        monkeypatch.setattr(provider._client, "post", post)

        messages: list[Message] = [
            {"role": "user", "content": "weather?"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [ToolCall(id="toolu_1", name="get_weather", arguments={"city": "Boston"})],
            },
            {"role": "tool", "tool_call_id": "toolu_1", "content": "Sunny, 70F"},
        ]
        provider.complete_with_tools(messages, _TOOLS, "system")

        sent = captured["payload"]["messages"]
        assert sent[1]["content"][0] == {"type": "tool_use", "id": "toolu_1", "name": "get_weather", "input": {"city": "Boston"}}
        assert sent[2]["role"] == "user"
        assert sent[2]["content"][0]["type"] == "tool_result"
        assert sent[2]["content"][0]["tool_use_id"] == "toolu_1"


class TestOpenAICompat:
    def test_parses_tool_call_arguments_as_json_string(self, monkeypatch):
        provider = OpenAICompatProvider(api_key="sk-test", model="gpt-test")
        monkeypatch.setattr(
            provider._client,
            "post",
            _fake_post(
                _response(
                    200,
                    {
                        "choices": [
                            {
                                "message": {
                                    "role": "assistant",
                                    "tool_calls": [
                                        {
                                            "id": "call_1",
                                            "function": {
                                                "name": "get_weather",
                                                "arguments": '{"city": "Boston"}',
                                            },
                                        }
                                    ],
                                }
                            }
                        ]
                    },
                )
            ),
        )

        turn = provider.complete_with_tools([{"role": "user", "content": "weather?"}], _TOOLS, "system")

        assert turn.tool_calls == [ToolCall(id="call_1", name="get_weather", arguments={"city": "Boston"})]

    def test_tool_result_uses_tool_role(self, monkeypatch):
        provider = OpenAICompatProvider(api_key="sk-test", model="gpt-test")
        captured = {}

        def post(url, json):
            captured["payload"] = json
            return _response(200, {"choices": [{"message": {"role": "assistant", "content": "done"}}]})

        monkeypatch.setattr(provider._client, "post", post)

        messages: list[Message] = [
            {"role": "user", "content": "weather?"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [ToolCall(id="call_1", name="get_weather", arguments={"city": "Boston"})],
            },
            {"role": "tool", "tool_call_id": "call_1", "content": "Sunny, 70F"},
        ]
        provider.complete_with_tools(messages, _TOOLS, "system")

        sent = captured["payload"]["messages"]
        assert sent[3] == {"role": "tool", "tool_call_id": "call_1", "content": "Sunny, 70F"}
        assert sent[2]["tool_calls"][0]["function"]["arguments"] == '{"city": "Boston"}'
