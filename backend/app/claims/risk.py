class ClaimRiskClassifier:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def classify(
        self,
        claim_type: str,
        confidence: float,
        has_numbers: bool,
        has_temporal_values: bool,
    ) -> str:

        # Numerical and temporal claims are more
        # sensitive to factual errors.
        if confidence < 0.5:
            return self.HIGH

        if claim_type == "numerical":
            return self.HIGH

        if claim_type == "causal":
            return self.HIGH

        if has_numbers and has_temporal_values:
            return self.HIGH

        if confidence < 0.75:
            return self.MEDIUM

        if has_numbers or has_temporal_values:
            return self.MEDIUM

        return self.LOW