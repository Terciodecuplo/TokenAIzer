## MODIFIED Requirements

### Requirement: Pricing storage
The system SHALL persist model pricing data with the following fields: `model`, `input_price_per_million`, `output_price_per_million`, `cache_creation_price_per_million`, `cache_read_price_per_million`, `currency`, `updated_at`. The system SHALL seed default pricing rows for all supported models on database initialisation if the pricing table is empty. Subsequent writes SHALL use upsert semantics so that a pricing sync job can update rows without deleting existing data.

#### Scenario: Default pricing seeded on first run
- **WHEN** the backend starts and the `model_pricing` table is empty
- **THEN** one pricing row is inserted for each supported model
- **AND** each row contains non-zero `input_price_per_million` and `output_price_per_million` values

#### Scenario: Seed is idempotent on subsequent runs
- **WHEN** the backend starts and pricing rows already exist
- **THEN** no pricing rows are overwritten or duplicated

#### Scenario: Pricing row upserted
- **WHEN** `upsert_pricing` is called with a model that already has a pricing row
- **THEN** the existing row is updated in place
- **AND** no duplicate rows are created

#### Scenario: Pricing data unavailable
- **GIVEN** a future pricing sync job cannot reach the external source
- **WHEN** the sync job runs
- **THEN** the last persisted pricing data is preserved
- **AND** no pricing row is deleted or overwritten with null values

### Requirement: Query support
The system SHALL support querying usage events filtered by `model`, `date_from`, `date_to`, and `source` (`proxy` | `manual`). All filter parameters SHALL be optional and combinable.

#### Scenario: Filter by source
- **WHEN** `get_usage_history` is called with `source="proxy"`
- **THEN** only rows where `source = 'proxy'` are returned
- **AND** rows with `source = 'manual'` are excluded

#### Scenario: Filter by model and date range
- **WHEN** `get_usage_history` is called with `model`, `date_from`, and `date_to`
- **THEN** only rows matching all three conditions are returned

#### Scenario: No filters returns all events
- **WHEN** `get_usage_history` is called with no filter arguments
- **THEN** all usage events are returned up to the `limit`
