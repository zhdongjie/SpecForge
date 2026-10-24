"""Stage-aware failures retain the actionable cause across CLI and repair boundaries."""


class VerificationError(RuntimeError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(f"{stage}: {message}")


class RepairNotApplicable(RuntimeError):
    pass
