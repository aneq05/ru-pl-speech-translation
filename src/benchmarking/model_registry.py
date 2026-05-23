from __future__ import annotations

from benchmarking.models import (
    ASRModel,
    ASRModelUnavailableError,
    EmptyASRModel,
    FasterWhisperASRModel,
    HFTransformersASRModel,
    SidecarASRModel,
    WhisperASRModel,
)

DEFAULT_MODEL_IDS = [
    "whisper:small",
    "faster-whisper:small",
    "hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian",
    "hf:jonatasgrosman/wav2vec2-xls-r-1b-russian",
]
SUPPORTED_MODEL_HINT = (
    "Supported formats: whisper:<size>, faster-whisper:<size>, hf:<huggingface_model_id>, "
    "dummy:empty, dummy:sidecar."
)


def create_model(
    model_id: str,
    *,
    language: str = "ru",
    device: str = "cpu",
) -> ASRModel:
    if model_id == "dummy:empty":
        return EmptyASRModel()

    if model_id == "dummy:sidecar":
        return SidecarASRModel()

    if model_id.startswith("hf:"):
        model_name = model_id.split(":", maxsplit=1)[1]
        return HFTransformersASRModel(model_name=model_name, device=device)

    if model_id.startswith("whisper:"):
        model_size = model_id.split(":", maxsplit=1)[1]
        return WhisperASRModel(model_size=model_size, language=language, device=device)

    if model_id.startswith("faster-whisper:"):
        model_size = model_id.split(":", maxsplit=1)[1]
        return FasterWhisperASRModel(model_size=model_size, language=language, device=device)

    raise ValueError(f"Unknown model id '{model_id}'. {SUPPORTED_MODEL_HINT}")


def create_models(
    model_ids: list[str],
    *,
    language: str = "ru",
    device: str = "cpu",
) -> tuple[list[ASRModel], list[str]]:
    models: list[ASRModel] = []
    unavailable: list[str] = []
    for model_id in model_ids:
        try:
            models.append(create_model(model_id, language=language, device=device))
        except ASRModelUnavailableError:
            unavailable.append(model_id)
    if not models:
        raise RuntimeError(
            "None of requested models are available in current environment. "
            f"Unavailable: {unavailable}. {SUPPORTED_MODEL_HINT}"
        )
    return models, unavailable
