## ADDED Requirements

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
