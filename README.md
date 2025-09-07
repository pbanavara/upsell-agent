# Upsell Agent

A CrewAI-based agent that analyzes PostHog events to identify upsell opportunities.

## Features

- Fetches user events from PostHog API
- Reads events from local JSON files
- Analyzes user behavior patterns to identify upsell opportunities
- Creates detailed task recommendations for sales teams
- Uses CrewAI framework for intelligent agent orchestration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostHog credentials in `config.json`:
```json
{
  "posthog_api_key": "YOUR_POSTHOG_API_KEY_HERE",
  "posthog_project_id": "YOUR_POSTHOG_PROJECT_ID_HERE",
  "events_file": "events.json"
}
```

**Note**: You can use either API access OR file-based analysis. If you don't have PostHog API credentials, you can export events to a JSON file and use file-based analysis.

## Usage

### API-based Analysis
Run the agent with PostHog API access:
```bash
python crew_agent.py
```

### File-based Analysis
1. Export your PostHog events to a JSON file (e.g., `events.json`)
2. Update `config.json` to point to your events file:
```json
{
  "events_file": "path/to/your/events.json"
}
```
3. Run the agent:
```bash
python crew_agent.py
```

### Supported File Formats

The agent supports multiple JSON file formats:

**Direct array of events:**
```json
[
  {
    "event": "product_viewed",
    "distinct_id": "user_001",
    "properties": {
      "product_name": "Premium Dashboard",
      "product_price": 299
    }
  }
]
```

**PostHog API response format:**
```json
{
  "results": [
    {
      "event": "product_viewed",
      "distinct_id": "user_001",
      "properties": {...}
    }
  ]
}
```

**Custom format with events key:**
```json
{
  "events": [
    {
      "event": "product_viewed",
      "distinct_id": "user_001",
      "properties": {...}
    }
  ]
}
```

## How it Works

The agent looks for patterns such as:
- Users viewing high-value products
- Users frequently using premium features
- Users reaching usage limits
- Users showing engagement with multiple product categories

For each opportunity found, it creates a detailed entry with:
- User ID
- Opportunity type
- Reasoning
- Recommended action

## Architecture

- **PostHogTool**: Custom tool to interact with PostHog API or read events from files
- **UpsellAgent**: CrewAI agent specialized in analyzing upsell opportunities
- **Crew**: Orchestrates the agent and task execution
- **Task**: Defines the analysis workflow and expected outputs

## Examples

Check out `sample_events.json` for an example of the expected event format. The sample file contains 1000+ realistic events with various user behaviors, product interactions, and upsell opportunity patterns including:

- **393 product views** - Users browsing different products and pricing tiers
- **311 feature usage events** - Users actively using premium and enterprise features  
- **199 page views** - Users navigating through pricing, features, and app pages
- **97 usage limit events** - Users hitting limits on basic plans

The agent successfully identifies patterns like:
- High-value product viewers ($599+ products)
- Heavy premium feature users (40+ usage counts)
- Users hitting usage limits on basic plans
- Cross-category engagement patterns

This provides a comprehensive test dataset for evaluating the upsell agent's analysis capabilities.