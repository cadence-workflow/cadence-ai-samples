"""Explicit operator messages and algorithm bounds for this controlled example."""

REVIEW = (
    "For each service, quote the ERROR log that supports the report. "
    "If a service has only warnings, say so. Do not infer an unobserved cause."
)
GUIDANCE = (
    "Follow the ERROR path from checkout through payments to ledger. "
    "Explain what the logs establish and what remains uncertain."
)
SECOND_REVIEW = (
    "The observed ERROR chain is checkout: payments authorize failed (503); "
    "payments: ledger connection pool exhausted and ledger call timed out; "
    "ledger: max connections reached for client payments. Inventory has WARN "
    "messages only. Revise the report to separate these observations. Do not "
    "claim inventory caused the failure. State that what triggered connection "
    "exhaustion is unknown, and quote the ERROR messages in errors_per_hop."
)
MAX_STEPS = 10
REPEAT_LIMIT = 1
