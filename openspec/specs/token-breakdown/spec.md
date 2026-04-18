# token-breakdown Specification

## Purpose
Provide a detailed per-model view of token consumption, separating
input, output, thinking, and cache token categories, and showing
their individual cost contributions.

## Requirements

### Requirement: Per-category breakdown
The system SHALL display for each model: input_tokens, output_tokens,
thinking_tokens, cache_creation_tokens, and cache_read_tokens as
separate values.

### Requirement: Cost per category
The system SHALL display the estimated cost contribution of each
token category separately, using the stored pricing for that model.

### Requirement: Thinking tokens visibility
The system SHALL only display the thinking_tokens row for models
that support extended thinking (claude-opus-4-6, claude-sonnet-4-6).

### Requirement: Percentage distribution
The system SHALL display each token category as a percentage of
the model's total tokens, visualised as a horizontal bar.

### Requirement: Model selector
The system SHALL allow the user to select which model to inspect
in detail from a list of all models with recorded activity.

### Requirement: Period filter
The system SHALL allow filtering the breakdown by time period:
today, last 7 days, last 30 days, and all time.

#### Scenario: Model with thinking tokens selected
- GIVEN usage events with thinking_tokens > 0 exist for a model
- WHEN the user selects that model in the breakdown view
- THEN the thinking_tokens row is visible with its value and cost
- AND thinking tokens are included in the percentage distribution

#### Scenario: Model without thinking tokens selected
- GIVEN a model has no thinking_tokens recorded
- WHEN the user selects that model in the breakdown view
- THEN the thinking_tokens row is not rendered
- AND the percentage distribution covers only the present categories

#### Scenario: Period filter applied
- GIVEN usage events exist across multiple days
- WHEN the user selects "last 7 days"
- THEN all values update to reflect only events within that range
- AND the percentage distribution recalculates accordingly