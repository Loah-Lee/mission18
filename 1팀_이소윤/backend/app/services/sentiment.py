import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

HF_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".hf-cache"
os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(HF_CACHE_DIR / "hub"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(HF_CACHE_DIR / "transformers"))

import torch
from huggingface_hub import hf_hub_download
from transformers import AutoConfig, AutoModel, AutoTokenizer

MODEL_ID = "monologg/koelectra-small-finetuned-sentiment"
NEUTRAL_MARGIN_THRESHOLD = 0.35
REVIEW_PROMPT_NEUTRAL_BAND = 0.25
MELANCHOLY_CUES = (
    "슬프",
    "눈물",
    "먹먹",
    "아프",
    "아련",
    "쓸쓸",
    "그립",
    "서글프",
    "마음",
    "가슴",
    "여운",
)
COMPLAINT_CUES = (
    "지루",
    "실망",
    "별로",
    "최악",
    "불편",
    "어색",
    "진부",
    "뻔하",
    "재미없",
    "허술",
    "산만",
    "억지",
)
CONTRAST_NEGATIVE_PATTERNS = (
    "좋다고 하지만",
    "최고라고 하는데",
    "명작인 걸 이해해보려고",
    "명작이 될 수는 없다",
    "봤음에도",
    "보는데 모두 실패",
    "하지만 나는",
    "좋다는데",
    "어려운 영화가",
)
POSITIVE_REVIEW_CUES = (
    ("좋", 1.0),
    ("추천", 1.5),
    ("명작", 2.0),
    ("인상적", 1.2),
    ("감동", 1.4),
    ("여운", 1.2),
    ("아름답", 1.3),
    ("훌륭", 1.5),
    ("완성도", 1.2),
    ("몰입", 1.0),
    ("재밌", 1.0),
    ("재미있", 1.0),
    ("다시 보고", 1.3),
    ("기억에 남", 1.1),
    ("섬세", 1.1),
    ("죽인다", 2.0),
    ("걸작", 2.0),
    ("세련", 1.2),
)
NEGATIVE_REVIEW_CUES = (
    ("지루", 1.6),
    ("실망", 1.8),
    ("별로", 1.7),
    ("최악", 3.0),
    ("불편", 1.6),
    ("어색", 1.4),
    ("진부", 1.8),
    ("뻔하", 1.6),
    ("재미없", 2.0),
    ("허술", 1.8),
    ("산만", 1.6),
    ("억지", 1.8),
    ("실패", 2.0),
    ("후회", 1.8),
    ("비추", 2.0),
    ("짜증", 2.2),
    ("싫", 2.0),
    ("최악", 3.0),
    ("혐오", 3.0),
    ("공감되지", 2.5),
    ("공감이 안", 2.5),
    ("강요", 2.2),
    ("신파", 2.0),
    ("왜 유명한거지", 2.5),
    ("어쩌라고", 3.0),
    ("명작이 될 수는 없다", 2.5),
)


def _get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@lru_cache(maxsize=1)
def _get_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=str(HF_CACHE_DIR))


@lru_cache(maxsize=1)
def _get_model_parts():
    device = _get_device()
    config = AutoConfig.from_pretrained(MODEL_ID, cache_dir=str(HF_CACHE_DIR))
    backbone = AutoModel.from_pretrained(MODEL_ID, cache_dir=str(HF_CACHE_DIR))
    classifier = torch.nn.Linear(config.hidden_size, config.num_labels)

    weights_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename="pytorch_model.bin",
        cache_dir=str(HF_CACHE_DIR),
    )
    state_dict = torch.load(weights_path, map_location="cpu")
    classifier.weight.data.copy_(state_dict["classifier.weight"])
    classifier.bias.data.copy_(state_dict["classifier.bias"])

    backbone.eval().to(device)
    classifier.eval().to(device)
    return backbone, classifier, config, device


def _resolve_sentiment(probabilities: torch.Tensor, config) -> tuple[str, float]:
    negative_prob = float(probabilities[0].item())
    positive_prob = float(probabilities[1].item())
    margin = abs(positive_prob - negative_prob)

    if margin < NEUTRAL_MARGIN_THRESHOLD:
        return "neutral", margin

    predicted_id = int(torch.argmax(probabilities).item())
    return config.id2label[predicted_id].lower(), max(positive_prob, negative_prob)


def _to_five_point_score(label: str, strength: float, positive_prob: float) -> float:
    if label == "positive":
        score = 3.0 + (strength * 2.0)
    elif label == "negative":
        score = 3.0 - (strength * 2.0)
    else:
        # Keep neutral reviews close to 3.0 while preserving a slight lean.
        tilt = (positive_prob - 0.5) * 2.0
        score = 3.0 + (tilt * 0.4)
    return round(min(max(score, 1.0), 5.0), 2)


def _adjust_for_review_context(
    text: str,
    label: str,
    strength: float,
    positive_prob: float,
) -> tuple[str, float]:
    normalized = text.strip()
    has_melancholy_cue = any(token in normalized for token in MELANCHOLY_CUES)
    has_complaint_cue = any(token in normalized for token in COMPLAINT_CUES)

    # Movie reviews often use sad language to praise emotional impact.
    # If the model predicts negative without complaint language, soften it to neutral.
    if label == "negative" and has_melancholy_cue and not has_complaint_cue:
        return "neutral", max(strength * 0.5, 0.2)

    return label, strength


def _classify_review_evaluation_prompt(text: str) -> tuple[str, float]:
    normalized = text.strip()
    positive_score = sum(weight for token, weight in POSITIVE_REVIEW_CUES if token in normalized)
    negative_score = sum(weight for token, weight in NEGATIVE_REVIEW_CUES if token in normalized)
    melancholy_hits = sum(token in normalized for token in MELANCHOLY_CUES)
    has_contrastive_negative = any(pattern in normalized for pattern in CONTRAST_NEGATIVE_PATTERNS)

    if has_contrastive_negative and negative_score > 0:
        strength = min(1.0, 0.7 + max(0.0, negative_score - positive_score) * 0.08)
        return "negative", strength

    if negative_score - positive_score >= 0.9:
        strength = min(1.0, 0.55 + (negative_score - positive_score) * 0.1)
        return "negative", strength

    if positive_score - negative_score >= 0.9:
        strength = min(1.0, 0.55 + (positive_score - negative_score) * 0.1)
        return "positive", strength

    if melancholy_hits > 0 and negative_score == 0:
        return "neutral", 0.35

    return "neutral", 0.2


def _blend_review_evaluation(
    model_label: str,
    model_strength: float,
    review_label: str,
    review_strength: float,
) -> tuple[str, float]:
    if review_label == model_label:
        return review_label, max(model_strength, review_strength)

    if review_label == "neutral" and model_label in {"positive", "negative"}:
        if model_strength < 0.8:
            return "neutral", max(review_strength, model_strength * 0.5)
        return model_label, model_strength

    if model_label == "neutral" and review_label in {"positive", "negative"}:
        return review_label, review_strength

    if review_label in {"positive", "negative"} and model_label in {"positive", "negative"}:
        gap = abs(review_strength - model_strength)
        if gap <= REVIEW_PROMPT_NEUTRAL_BAND:
            return review_label, max(review_strength, model_strength)
        return "neutral", 0.3

    return model_label, model_strength


def analyze_sentiment(text: str) -> dict:
    tokenizer = _get_tokenizer()
    backbone, classifier, config, device = _get_model_parts()

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        outputs = backbone(**encoded)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        logits = classifier(cls_embedding)
        probabilities = torch.softmax(logits, dim=-1)[0]
        positive_prob = float(probabilities[1].item())

    model_label, model_strength = _resolve_sentiment(probabilities, config)
    model_label, model_strength = _adjust_for_review_context(
        text,
        model_label,
        model_strength,
        positive_prob,
    )
    review_label, review_strength = _classify_review_evaluation_prompt(text)
    label, strength = _blend_review_evaluation(
        model_label,
        model_strength,
        review_label,
        review_strength,
    )
    return {
        "label": label,
        "score": _to_five_point_score(label, strength, positive_prob),
        "model": MODEL_ID,
        "confidence": round(max(float(probabilities[0].item()), positive_prob), 4),
    }
