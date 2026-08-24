import re
from typing import List

from backend.app.extraction.models import (
    ExtractedDocument,
)

from backend.app.claims.models import (
    Claim,
    Entity,
    NumberValue,
    TemporalValue,
    Evidence,
)

from backend.app.claims.risk import (
    ClaimRiskClassifier,
)


class ClaimExtractor:

    # --------------------------------------------------
    # BASIC PATTERNS
    # --------------------------------------------------

    NUMBER_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?(?:\s?%|\s?(?:MB|GB|KB|km|m|cm|mm|"
        r"kg|g|mg|seconds?|minutes?|hours?|days?|weeks?|"
        r"months?|years?))?\b",
        re.IGNORECASE,
    )

    YEAR_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b"
    )

    DATE_PATTERN = re.compile(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    )

    # --------------------------------------------------
    # INITIALIZE
    # --------------------------------------------------

    def __init__(self):

        self.risk_classifier = (
            ClaimRiskClassifier()
        )

    # ==================================================
    # MAIN EXTRACTION
    # ==================================================

    def extract(
        self,
        document: ExtractedDocument,
    ) -> List[Claim]:

        claims = []

        claim_id = 1

        for page in document.pages:

            page_claims = self._extract_page_claims(
                page.text,
                page.page_number,
            )

            for claim in page_claims:

                claim.claim_id = claim_id

                claims.append(
                    claim
                )

                claim_id += 1

        return claims

    # ==================================================
    # PAGE CLAIM EXTRACTION
    # ==================================================

    def _extract_page_claims(
        self,
        text: str,
        page_number: int,
    ) -> List[Claim]:

        claims = []

        sentences = self._split_sentences(
            text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) < 20:
                continue

            numbers = self._extract_numbers(
                sentence
            )

            temporal_values = (
                self._extract_temporal_values(
                    sentence
                )
            )

            entities = self._extract_entities(
                sentence
            )

            claim_type = self._determine_claim_type(
                sentence,
                numbers,
                temporal_values,
            )

            confidence = self._estimate_confidence(
                sentence,
                entities,
                numbers,
                temporal_values,
            )

            risk = self.risk_classifier.classify(
                claim_type=claim_type,
                confidence=confidence,
                has_numbers=bool(numbers),
                has_temporal_values=bool(
                    temporal_values
                ),
            )

            evidence = Evidence(
                page_number=page_number,
                text=sentence,
            )

            claims.append(
                Claim(
                    claim_id=0,
                    claim_text=sentence,
                    claim_type=claim_type,
                    entities=entities,
                    numbers=numbers,
                    temporal_values=temporal_values,
                    evidence=[evidence],
                    confidence=confidence,
                    risk=risk,
                )
            )

        return claims

    # ==================================================
    # SENTENCE SPLITTING
    # ==================================================

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> List[str]:

        normalized = (
            text
            .replace("\n", " ")
            .replace("•", ". ")
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            normalized,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    # ==================================================
    # NUMBER EXTRACTION
    # ==================================================

    def _extract_numbers(
        self,
        text: str,
    ) -> List[NumberValue]:

        results = []

        for match in self.NUMBER_PATTERN.finditer(
            text
        ):

            raw = match.group(0).strip()

            numeric_match = re.search(
                r"\d+(?:\.\d+)?",
                raw,
            )

            value = None

            if numeric_match:

                try:
                    value = float(
                        numeric_match.group(0)
                    )
                except ValueError:
                    value = None

            unit = raw[
                numeric_match.end():
            ].strip() if numeric_match else None

            results.append(
                NumberValue(
                    text=raw,
                    value=value,
                    unit=unit or None,
                )
            )

        return results

    # ==================================================
    # TEMPORAL EXTRACTION
    # ==================================================

    def _extract_temporal_values(
        self,
        text: str,
    ) -> List[TemporalValue]:

        values = []

        patterns = [
            self.YEAR_PATTERN,
            self.DATE_PATTERN,
        ]

        for pattern in patterns:

            for match in pattern.finditer(
                text
            ):

                values.append(
                    TemporalValue(
                        text=match.group(0)
                    )
                )

        return values

    # ==================================================
    # BASIC ENTITY EXTRACTION
    # ==================================================

    @staticmethod
    def _extract_entities(
        text: str,
    ) -> List[Entity]:

        entities = []

        # Basic proper-noun detection.
        #
        # This is intentionally conservative.
        # A dedicated NER component can replace
        # this later.

        matches = re.findall(
            r"\b[A-Z][A-Za-z0-9-]{2,}"
            r"(?:\s+[A-Z][A-Za-z0-9-]{2,})*",
            text,
        )

        seen = set()

        for match in matches:

            cleaned = match.strip()

            if cleaned in seen:
                continue

            seen.add(cleaned)

            entities.append(
                Entity(
                    text=cleaned,
                    entity_type="PROPER_NOUN",
                )
            )

        return entities

    # ==================================================
    # CLAIM TYPE
    # ==================================================

    @staticmethod
    def _determine_claim_type(
        sentence: str,
        numbers: List[NumberValue],
        temporal_values: List[TemporalValue],
    ) -> str:

        lowered = sentence.lower()

        if any(
            word in lowered
            for word in [
                "because",
                "therefore",
                "causes",
                "caused",
                "leads to",
                "resulted in",
            ]
        ):

            return "causal"

        if numbers:

            return "numerical"

        if temporal_values:

            return "temporal"

        return "factual"

    # ==================================================
    # CONFIDENCE
    # ==================================================

    @staticmethod
    def _estimate_confidence(
        sentence: str,
        entities: List[Entity],
        numbers: List[NumberValue],
        temporal_values: List[TemporalValue],
    ) -> float:

        score = 0.7

        if len(sentence) >= 40:
            score += 0.05

        if entities:
            score += 0.05

        if numbers:
            score += 0.05

        if temporal_values:
            score += 0.05

        return min(
            round(score, 3),
            1.0,
        )