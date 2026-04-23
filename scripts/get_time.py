# Tier 3 fallback for the Cortex `get_current_time` contract.
# Returns current system time in ISO 8601 format with timezone offset.
# No arguments. No network. Stateless. Fast.
# Output example: 2026-04-23T19:09:38-04:00

import datetime

print(datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat())
