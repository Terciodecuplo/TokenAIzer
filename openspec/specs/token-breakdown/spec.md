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

### Requirement: Per-category breakdown view
The system SHALL render a "Token breakdown" section in the dashboard containing a model selector and period filter. When a model and period are selected, the section SHALL display one row per token category (input, output, thinking, cache_creation, cache_read) showing: token count, estimated cost for that category, and a horizontal percentage bar proportional to total tokens consumed.

#### Scenario: Model and period selected
- **WHEN** the user selects a model and a time period
- **THEN** the breakdown section displays one row per category with token count, cost, and a proportional bar

#### Scenario: No data for selected period
- **WHEN** no usage events exist for the selected model and period
- **THEN** all rows display zero counts and costs, and the bars are empty

### Requirement: Thinking tokens conditional display
The breakdown section SHALL render the thinking_tokens row only when the selected model's thinking_tokens value for the selected period is greater than zero.

#### Scenario: Model with thinking tokens
- **WHEN** the selected model has thinking_tokens > 0 for the selected period
- **THEN** the thinking_tokens row is visible with its count, cost, and bar

#### Scenario: Model without thinking tokens
- **WHEN** the selected model has thinking_tokens == 0 for the selected period
- **THEN** the thinking_tokens row is not rendered

### Requirement: Period filter
The breakdown section SHALL provide four preset period options: Today, Last 7 days, Last 30 days, and All time. Selecting a period SHALL immediately update all displayed values.

#### Scenario: Period changed
- **WHEN** the user selects a different period
- **THEN** all token counts, costs, and bars update to reflect only events within that period

### Requirement: Model selector
The breakdown section SHALL provide a selector listing all models present in the pricing table. The first model SHALL be selected by default on load.

#### Scenario: Model changed
- **WHEN** the user selects a different model from the selector
- **THEN** the breakdown rows update to reflect usage for that model in the current period