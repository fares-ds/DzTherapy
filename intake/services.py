"""AI intake assistant — wraps Anthropic Claude to interview a visitor and
recommend approved therapists.

Design choices:
- The model receives the *current list of approved therapists* in its system
  prompt as JSON, then recommends 2–3 by slug. We never let the model invent
  therapists or surface unapproved ones; we filter its output against the
  authoritative DB.
- Empty `ANTHROPIC_API_KEY` → service returns a deterministic fallback that
  recommends the 3 most-recently-approved therapists. Keeps dev usable.
- Per PRD §12 the assistant must never claim to *be* a therapist or replace one.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable

from django.conf import settings

from therapists.models import TherapistProfile, VerificationStatus

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Vous êtes un assistant d'orientation pour DzTherapy, une plateforme algérienne
de mise en relation avec des psychologues vérifié·e·s.

Votre rôle :
1. Accueillir la personne avec chaleur et discrétion (en français).
2. Poser 3 à 5 questions courtes pour comprendre :
   - Ce qui l'amène (anxiété, burnout, relation, sommeil…) — sans diagnostic.
   - Préférence de genre du ou de la praticien·ne (sans préférence acceptée).
   - Préférence de langue (français, arabe, etc.).
3. Recommander 2 à 3 thérapeutes parmi la liste fournie ci-dessous, en
   expliquant brièvement pourquoi chacun pourrait correspondre.

Règles strictes :
- Vous n'êtes PAS un·e thérapeute. Ne donnez jamais de conseil clinique,
  de diagnostic, ni de plan de traitement.
- En cas de signaux de crise (idées suicidaires, danger immédiat) : indiquez
  immédiatement les numéros d'urgence (SOS Algérie : 0560 001 555 ; SAMU : 115)
  et invitez la personne à contacter les services d'urgence.
- Ne recommandez QUE les thérapeutes de la liste fournie, par leur slug.
- Soyez bref. Pas plus de 3 phrases par message tant que vous n'êtes pas
  arrivé·e à la recommandation finale.

Quand vous êtes prêt·e à recommander, terminez votre dernier message par
exactement le bloc :
<recommend>slug-1, slug-2, slug-3</recommend>
"""


def _approved_therapists_summary(limit: int = 30) -> list[dict]:
    """Compact JSON-serializable view of the approved roster. Capped to keep
    the prompt small."""
    qs = TherapistProfile.objects.filter(
        verification_status=VerificationStatus.APPROVED
    ).order_by("-created_at")[:limit]
    return [
        {
            "slug": t.slug,
            "full_name": t.full_name,
            "specialties": t.specialties,
            "languages": t.languages,
            "gender": t.gender,
            "session_price_dzd": t.session_price_dzd,
            "headline": t.headline,
        }
        for t in qs
    ]


def is_enabled() -> bool:
    return bool(settings.ANTHROPIC_API_KEY)


def reply(messages: list[dict]) -> str:
    """Given the conversation so far, ask Claude for the next assistant turn.

    Falls back to a static greeting / handoff text when no API key is set.
    `messages` is a list of {"role": "user"|"assistant", "content": str}.
    """
    if not is_enabled():
        return _fallback_reply(messages)

    try:
        import anthropic
    except ImportError:
        log.exception("anthropic SDK not installed; falling back")
        return _fallback_reply(messages)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    roster = _approved_therapists_summary()
    system = (
        SYSTEM_PROMPT
        + "\n\nThérapeutes approuvé·e·s actuellement disponibles :\n"
        + json.dumps(roster, ensure_ascii=False)
    )
    try:
        resp = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            system=system,
            max_tokens=600,
            messages=messages,
        )
        # Defensive: messages.create may return content blocks
        for block in resp.content:
            text = getattr(block, "text", None)
            if text:
                return text
        return _fallback_reply(messages)
    except Exception:
        log.exception("Anthropic call failed; falling back")
        return _fallback_reply(messages)


def _fallback_reply(messages: list[dict]) -> str:
    """Used when Anthropic is unavailable or fails. Deterministic, dev-safe."""
    turn = sum(1 for m in messages if m["role"] == "user")
    if turn == 0:
        return (
            "Bonjour. Je suis l'assistant d'orientation de DzTherapy. "
            "Pour vous suggérer un·e thérapeute adapté·e, dites-moi en quelques mots "
            "ce qui vous amène (par exemple : anxiété, burnout, sommeil, relation)."
        )
    if turn == 1:
        return (
            "Merci. Préférez-vous une thérapeute femme, un thérapeute homme, "
            "ou n'avez-vous pas de préférence ?"
        )
    if turn == 2:
        return (
            "Très bien. Et en quelle langue préférez-vous les séances "
            "(français, arabe, ou autre) ?"
        )
    # Recommendation turn
    slugs = [
        s
        for s in TherapistProfile.objects.filter(
            verification_status=VerificationStatus.APPROVED
        )
        .order_by("-created_at")
        .values_list("slug", flat=True)[:3]
    ]
    if not slugs:
        return (
            "Notre roster est en cours de constitution. "
            "Inscrivez-vous et nous vous notifierons dès que des thérapeutes "
            "correspondant à vos critères seront disponibles."
        )
    return (
        "Merci pour ces informations. Voici les profils que je vous suggère "
        f"d'examiner : <recommend>{', '.join(slugs)}</recommend>"
    )


def extract_recommended_slugs(text: str) -> list[str]:
    """Pull `<recommend>slug-1, slug-2</recommend>` from the model's output."""
    import re

    match = re.search(r"<recommend>(.*?)</recommend>", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    raw = match.group(1)
    return [s.strip() for s in raw.split(",") if s.strip()]


def filter_recommended_therapists(slugs: Iterable[str]) -> list[TherapistProfile]:
    """Hard authority gate: never surface a slug that isn't approved."""
    return list(
        TherapistProfile.objects.filter(
            slug__in=list(slugs), verification_status=VerificationStatus.APPROVED
        )
    )
