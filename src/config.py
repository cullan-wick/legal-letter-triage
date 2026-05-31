"""Configuration helpers with optional Weave support.

The scaffold must run before dependencies and API keys are installed, so imports
for third-party services stay optional here.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from time import perf_counter
from typing import Any, TypeVar


F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class Settings:
    weave_project: str = "legal-letter-triage"
    model_provider: str = "stub"
    model_name: str = "stub"
    anthropic_api_key: str = ""
    tavily_api_key: str = ""
    wandb_api_key: str = ""


def load_settings() -> Settings:
    return Settings(
        weave_project=os.getenv("WEAVE_PROJECT", "legal-letter-triage"),
        model_provider=os.getenv("MODEL_PROVIDER", "stub"),
        model_name=os.getenv("MODEL_NAME", "stub"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        wandb_api_key=os.getenv("WANDB_API_KEY", ""),
    )


def init_weave() -> None:
    settings = load_settings()
    if not settings.wandb_api_key:
        return

    try:
        import weave  # type: ignore
    except Exception:
        return

    try:
        weave.init(settings.weave_project)
    except Exception:
        return


def traced_op(name: str) -> Callable[[F], F]:
    """Decorate a function with Weave when available and record local latency."""

    def decorate(func: F) -> F:
        if load_settings().wandb_api_key:
            try:
                import weave  # type: ignore

                return weave.op(name=name)(func)  # type: ignore[return-value]
            except Exception:
                pass

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = round((perf_counter() - start) * 1000, 2)
            if isinstance(result, dict):
                result.setdefault("latency_ms", elapsed_ms)
            return result

        return wrapper  # type: ignore[return-value]

    return decorate
