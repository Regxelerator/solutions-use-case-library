import json
import re
import os
import yaml
import openai
from openai import AzureOpenAI
from pathlib import Path
from utils.schemas import MODEL_INPUT_SCHEMA


class LLMClientFactory:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER")
        if self.LLM_PROVIDER is None:
            raise EnvironmentError(
                "LLM PROVIDER environment variable not set in .env file"
            )
        self.config = self.load_config(Path("model_config.yml"))
        self.config = self.config.get(self.LLM_PROVIDER)
        self.clients_cache = {}

    def load_config(self, path: Path) -> dict:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def parse_llm_response(self, response_text):
        match = re.search(
            r"```json\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE
        )
        candidate = match.group(1) if match else response_text.strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
            else:
                return response_text.strip()
        except json.JSONDecodeError:
            return response_text.strip()

    def get_client(self, provider: str, deployment_name: str, _api_version=None):
        provider = provider.lower()
        if provider in self.clients_cache:
            return self.clients_cache[provider]

        if provider == "openai":
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "azure":
            if _api_version is None and os.getenv("AZURE_OPENAI_API_VERSION") is None:
                raise EnvironmentError("AZURE_API_VERSION variable not set")
            client = AzureOpenAI(
                azure_deployment=deployment_name,
                api_version=_api_version
                if _api_version
                else os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        self.clients_cache[provider] = client
        return client

    def get_schema(self, model_case):
        return MODEL_INPUT_SCHEMA.get(model_case)

    def chat_completion(self, model_case: str, messages: list, **kwargs):
        model_input_schema = None
        deployment_name = None
        model_api_version = None

        model_config = self.config.get(model_case)
        if not model_config:
            raise ValueError(f"Model config '{model_case}' not found")

        provider = self.LLM_PROVIDER.lower()
        if not provider:
            raise ValueError("Provider not defined.")

        if provider == "azure":
            model_input_schema = self.get_schema(model_case)
            model_name = model_config.get("model")
            model_api_version = model_config.get("api_version")
            deployment_name = model_config.get("deployment_name") or model_name
            if deployment_name is None:
                raise ValueError(
                    "Deployment_name or model_name are missing in model_config.yml"
                )

        client = self.get_client(
            provider, deployment_name, _api_version=model_api_version
        )
        known_keys = {"provider", "model"}
        params = {"messages": messages}
        if "model" in model_config:
            params["model"] = model_config["model"]
        extra_params = {k: v for k, v in model_config.items() if k not in known_keys}
        if provider == "azure":
            params["model"] = deployment_name
            extra_params.pop("deployment_name", None)
            extra_params.pop("api_version", None)

        if "response_format" in extra_params:
            if provider == "azure" and kwargs.get("json_schema"):
                extra_params["response_format"] = {
                    "type": extra_params["response_format"],
                    "json_schema": kwargs.get("json_schema"),
                }
            elif provider == "azure" and model_input_schema:
                extra_params["response_format"] = {
                    "type": extra_params["response_format"],
                    "json_schema": model_input_schema,
                }
            else:
                extra_params["response_format"] = {
                    "type": extra_params["response_format"]
                }

        if model_config.get("model_type") == "chat_model":
            extra_params.pop("reasoning_effort", None)
        elif model_config.get("model_type") == "reasoning_model":
            if not model_config.get("reasoning_effort"):
                raise ValueError(
                    "Model type 'reasoning_model' has missing parameter 'reasoning_effort'."
                )
            extra_params.pop("temperature", None)

        if extra_params.get("model_type") or not extra_params.get("model_type"):
            extra_params.pop("model_type", None)
        params.update(extra_params)

        response = client.chat.completions.create(**params)
        response_format = extra_params.get("response_format")
        if response_format and isinstance(response_format, dict):
            if (
                response_format.get("type") == "json_object"
                or response_format.get("type") == "json_schema"
            ):
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    return {}
        return response.choices[0].message.content

    def call_reasoning_model(self, prompt: str, config: dict) -> str:
        required_keys = ["model", "reasoning_effort", "response_format"]
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise KeyError(f"Missing config keys for reasoning_model: {missing}")
        response = openai.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort=config["reasoning_effort"],
            response_format=config["response_format"],
        )
        message = response.choices[0].message.content
        return message