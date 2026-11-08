# v0.0.10

## what's new

[ADD] Build-time translation validation now includes JavaScript reads as well as HTML.

## changelog

[FIX] Recognize translation keys passed through project-specific helper functions, including forwarded parameters, conditional literal arguments and template interpolations. No helper name is hardcoded.

[CHANGE] Analyze library and project JavaScript together. Unused-key warnings and missing-key errors now refer to HTML and JavaScript. Translation declarations, comments and unrelated strings do not count as uses.

[TEST] Add regression tests for translation reads, helper forwarding, missing/unused keys and duplicate declarations.
