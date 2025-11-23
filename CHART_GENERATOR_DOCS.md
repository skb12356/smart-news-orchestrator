# Chart Generation Agent - Complete Documentation

## 🎯 Overview

The **Chart Generation Agent** is an intelligent component of the IBM Watsonx Orchestrate news analysis pipeline. It automatically analyzes tabular data from news articles and generates appropriate visualizations using matplotlib.

## 📁 Files Created

### Core Components
1. **`tools/chart_generator.py`** - Chart generation engine
2. **`tools/chart_generator_tool.py`** - IBM Orchestrate @tool wrappers
3. **`agents/chart-generator-agent.yaml`** - Agent configuration
4. **`agents/chart_examples.py`** - Usage examples
5. **`agents/charts/`** - Output directory for generated charts

## 🚀 Features

### Intelligent Chart Type Detection
The agent automatically selects the best chart type based on:
- **Data structure** (columns, data types)
- **Context** (natural language instruction)
- **Pattern detection** (time series, categories, composition)

### Supported Chart Types
1. **Line Charts** - Time series trends
2. **Bar Charts** - Categorical comparisons
3. **Pie Charts** - Composition/market share
4. **Histograms** - Distribution analysis

### Chart Quality
- High resolution (150 DPI)
- Professional styling
- Clear labels and titles
- Appropriate sizing (10x6 or 10x8)
- Grid lines and legends

## 📊 Usage Examples

### Example 1: Basic Chart Generation
```python
from tools.chart_generator import ChartGenerator

data = [
    {"Quarter": "Q1", "Revenue": 120},
    {"Quarter": "Q2", "Revenue": 140},
    {"Quarter": "Q3", "Revenue": 135},
    {"Quarter": "Q4", "Revenue": 150}
]

generator = ChartGenerator()
result = generator.generate_chart(
    data, 
    "Quarterly revenue for Apple Inc"
)

print(result)
# {
#   "chart_type": "line",
#   "file_path": "/path/to/chart_line_20251123.png",
#   "description": "Line chart showing trends in Quarterly revenue..."
# }
```

### Example 2: Using IBM Orchestrate Tools
```python
from tools.chart_generator_tool import (
    generate_chart_from_table,
    create_trend_chart,
    create_comparison_chart
)

# Auto-detect chart type
result = generate_chart_from_table(
    data='[{"Product": "iPhone", "Sales": 850}, ...]',
    instruction="Product sales comparison"
)

# Specific chart types
trend_chart = create_trend_chart(
    time_series_data='[{"Month": "Jan", "Price": 150}, ...]',
    metric_name="Stock Price"
)

comparison = create_comparison_chart(
    comparison_data='[{"Company": "Apple", "Revenue": 394}, ...]',
    comparison_title="Tech company revenue"
)
```

### Example 3: From News Article Tables
```python
from tools.chart_generator_tool import generate_chart_from_article_table

# Extract table from article's relevant_tables field
article_table = article['relevant_tables'][0]

result = generate_chart_from_article_table(
    table_data=json.dumps(article_table),
    article_context="Quarterly earnings comparison"
)
```

## 🔧 IBM Watsonx Orchestrate Integration

### Agent Configuration (`chart-generator-agent.yaml`)

```yaml
kind: native
spec_version: v1
name: chart-generator-agent
description: Chart Generation Agent for news analysis

llm:
  model_id: watsonx/meta-llama/llama-3-2-90b-vision-instruct
  parameters:
    temperature: 0.7
    max_tokens: 2000

tools:
  - generate_chart_from_table
  - generate_chart_from_article_table
  - create_trend_chart
  - create_comparison_chart
  - create_composition_chart
```

### Available Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `generate_chart_from_table` | Auto-detect chart type | JSON data + instruction | Chart metadata |
| `generate_chart_from_article_table` | Charts from news tables | Table data + context | Chart metadata |
| `create_trend_chart` | Time-series trends | Time series data + metric | Line chart |
| `create_comparison_chart` | Category comparison | Comparison data + title | Bar chart |
| `create_composition_chart` | Market share/composition | Composition data + title | Pie chart |

## 🎨 Chart Decision Logic

### Automatic Detection
```
IF data has date/time column AND numeric columns
  → Line Chart (time series)

ELSE IF data has "percentage" or "share" in instruction
  → Pie Chart (composition)

ELSE IF data has categorical + numeric columns
  → Bar Chart (comparison)

ELSE IF instruction mentions "distribution" or "histogram"
  → Histogram

ELSE
  → Bar Chart (default)
```

## 📂 Output Structure

### File Naming Convention
```
chart_<type>_<timestamp>.png

Examples:
- chart_line_20251123_050429.png
- chart_bar_20251123_050429.png
- chart_pie_20251123_050429.png
```

### Output Directory
```
hackathon-IBM/
└── agents/
    └── charts/
        ├── chart_line_*.png
        ├── chart_bar_*.png
        └── chart_pie_*.png
```

### Return Format
```json
{
  "chart_type": "line",
  "file_path": "/absolute/path/to/chart.png",
  "description": "Line chart showing trends in quarterly revenue"
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Test core chart generator
python tools/chart_generator.py

# Test IBM Orchestrate tools
python tools/chart_generator_tool.py

# Run comprehensive examples
python agents/chart_examples.py
```

### Expected Output
```
=== Test 1: Line Chart ===
{
  "chart_type": "line",
  "file_path": "C:\\...\\chart_line_20251123.png",
  "description": "Line chart showing trends in ..."
}

✅ All charts generated successfully!
📁 Charts saved to: agents/charts/
```

## 🔗 Integration with Risk Scorer

The chart generator can visualize risk assessment data:

```python
# Example: Visualize risk scores
from tools.chart_generator import ChartGenerator
import json

# Load risk assessment results
with open('agents/risk_agent/risk_assessment_results.json') as f:
    assessment = json.load(f)

# Extract sentiment distribution
sentiment_dist = assessment['summary']['sentiment_distribution']
sentiment_data = [
    {"Sentiment": k, "Count": v}
    for k, v in sentiment_dist.items()
]

# Generate pie chart
generator = ChartGenerator()
result = generator.generate_chart(
    sentiment_data,
    "Sentiment Distribution from Risk Assessment",
    chart_type="pie"
)
```

## 📝 Dependencies

Added to `req.txt`:
```
matplotlib==3.10.0
```

## 🎯 Use Cases

1. **Risk Assessment Visualization**
   - Risk score trends over time
   - Sentiment distribution
   - Category breakdown

2. **News Article Analytics**
   - Generate charts from article tables
   - Visualize financial data
   - Compare metrics across companies

3. **Market Analysis**
   - Stock price trends
   - Market share composition
   - Quarterly revenue comparisons

4. **Automated Reporting**
   - Embed charts in generated reports
   - Reference charts by file path
   - Persistent storage for later use

## 🚦 Error Handling

### Invalid Data
```json
{
  "error": "Invalid or empty dataset provided.",
  "details": "Data must be a non-empty list of dictionaries"
}
```

### Chart Generation Failure
```json
{
  "error": "Failed to generate chart",
  "details": "Error message with details"
}
```

## 🎓 Best Practices

1. **Provide Context**: Always include instruction parameter for better chart selection
2. **Use Specific Tools**: Use specialized tools (create_trend_chart, etc.) when you know the chart type
3. **Check Output**: Verify file_path exists before embedding in articles
4. **Clean Data**: Ensure data is properly formatted as list of dictionaries
5. **Meaningful Labels**: Use clear column names in your data

## 📊 Sample Charts Generated

The test suite generates:
- ✅ Line chart: Quarterly revenue trends
- ✅ Bar chart: Product sales comparison
- ✅ Pie chart: Market share distribution
- ✅ Risk score visualizations
- ✅ Sentiment distribution charts

All charts saved to: `agents/charts/`

## 🔮 Future Enhancements

Potential additions:
- Multi-line charts with legends
- Stacked bar charts
- Area charts
- Heatmaps for correlation matrices
- Custom color schemes
- Interactive charts (plotly)
- Chart annotations
- Export to multiple formats (SVG, PDF)

---

**Ready for IBM Watsonx Orchestrate Deployment** 🚀

The Chart Generation Agent is fully integrated with the news analysis pipeline and ready to visualize data from scraped articles, risk assessments, and market trends.
