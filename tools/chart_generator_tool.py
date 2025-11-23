"""
IBM Watsonx Orchestrate Tool: Chart Generator
@tool decorated functions for chart generation that can be called by LLM agents.
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from pathlib import Path
import sys
import json

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(parent_dir))

from chart_generator import ChartGenerator


@tool
def generate_chart_from_table(
    data: str,
    instruction: str = "",
    chart_type: str = "auto",
    article_id: str = "",
    chart_number: int = 1
) -> str:
    """
    Generate a chart from tabular data for embedding in news articles.
    
    Args:
        data: JSON string of tabular data (list of dicts)
        instruction: Natural language description of what the data represents
        chart_type: Type of chart (auto, line, bar, pie, histogram)
        article_id: Article identifier (e.g., "article1", "article2") for naming
        chart_number: Chart number within article (e.g., 1, 2, 3)
    
    Returns:
        JSON string with chart_type, file_path, and description
    
    Example:
        data = '[{"Quarter": "Q1", "Revenue": 120}, {"Quarter": "Q2", "Revenue": 140}]'
        instruction = "Quarterly revenue for Apple Inc"
        result = generate_chart_from_table(data, instruction, "auto", "article1", 1)
        # Saves as: article1_1.png
    """
    generator = ChartGenerator()
    result = generator.generate_chart(
        data, instruction, chart_type, 
        article_id if article_id else None,
        chart_number if chart_number else None
    )
    return json.dumps(result, indent=2)


@tool
def generate_chart_from_article_table(
    table_data: str,
    article_context: str = "",
    article_id: str = "",
    chart_number: int = 1
) -> str:
    """
    Generate a chart from a table extracted from a news article.
    Automatically detects the best chart type based on data structure.
    
    Args:
        table_data: JSON string of table data from article (list of dicts)
        article_context: Brief context about the article topic
        article_id: Article identifier for naming (e.g., "article1")
        chart_number: Chart number within article (1, 2, 3...)
    
    Returns:
        JSON string with chart metadata (type, file_path, description)
    
    Example:
        table_data = '[{"Company": "Apple", "Revenue": 394}, {"Company": "Samsung", "Revenue": 243}]'
        article_context = "Tech company quarterly earnings comparison"
        result = generate_chart_from_article_table(table_data, article_context, "article2", 1)
        # Saves as: article2_1.png
    """
    generator = ChartGenerator()
    
    # Auto-detect chart type
    result = generator.generate_chart(
        table_data, article_context, chart_type="auto",
        article_id=article_id if article_id else None,
        chart_number=chart_number if chart_number else None
    )
    return json.dumps(result, indent=2)


@tool
def create_trend_chart(
    time_series_data: str,
    metric_name: str,
    article_id: str = "",
    chart_number: int = 1
) -> str:
    """
    Create a line chart specifically for time-series trend analysis.
    
    Args:
        time_series_data: JSON string with time-based data points
        metric_name: Name of the metric being tracked (e.g., "Stock Price", "Revenue")
        article_id: Article identifier for naming (e.g., "article1")
        chart_number: Chart number within article
    
    Returns:
        JSON string with chart metadata
    
    Example:
        data = '[{"Date": "Jan", "Price": 150}, {"Date": "Feb", "Price": 165}]'
        metric = "Apple Stock Price"
        result = create_trend_chart(data, metric, "article3", 1)
        # Saves as: article3_1.png
    """
    generator = ChartGenerator()
    instruction = f"{metric_name} trend over time"
    result = generator.generate_chart(
        time_series_data, instruction, chart_type="line",
        article_id=article_id if article_id else None,
        chart_number=chart_number if chart_number else None
    )
    return json.dumps(result, indent=2)


@tool
def create_comparison_chart(
    comparison_data: str,
    comparison_title: str,
    article_id: str = "",
    chart_number: int = 1
) -> str:
    """
    Create a bar chart for comparing categories or entities.
    
    Args:
        comparison_data: JSON string with categorical comparison data
        comparison_title: Title describing what's being compared
        article_id: Article identifier for naming (e.g., "article1")
        chart_number: Chart number within article
    
    Returns:
        JSON string with chart metadata
    
    Example:
        data = '[{"Product": "iPhone", "Sales": 850}, {"Product": "Mac", "Sales": 420}]'
        title = "Product sales by category"
        result = create_comparison_chart(data, title, "article4", 2)
        # Saves as: article4_2.png
    """
    generator = ChartGenerator()
    result = generator.generate_chart(
        comparison_data, comparison_title, chart_type="bar",
        article_id=article_id if article_id else None,
        chart_number=chart_number if chart_number else None
    )
    return json.dumps(result, indent=2)


@tool
def create_composition_chart(
    composition_data: str,
    composition_title: str,
    article_id: str = "",
    chart_number: int = 1
) -> str:
    """
    Create a pie chart showing composition or market share.
    
    Args:
        composition_data: JSON string with parts-of-whole data
        composition_title: Title describing the composition
        article_id: Article identifier for naming (e.g., "article1")
        chart_number: Chart number within article
    
    Returns:
        JSON string with chart metadata
    
    Example:
        data = '[{"Segment": "iPhone", "Percentage": 52}, {"Segment": "Services", "Percentage": 23}]'
        title = "Apple revenue by segment"
        result = create_composition_chart(data, title, "article5", 1)
        # Saves as: article5_1.png
    """
    generator = ChartGenerator()
    result = generator.generate_chart(
        composition_data, composition_title, chart_type="pie",
        article_id=article_id if article_id else None,
        chart_number=chart_number if chart_number else None
    )
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Test the tools
    print("Testing Chart Generator Tools\n")
    
    # Test 1: Generic chart generation
    test_data = json.dumps([
        {"Quarter": "Q1", "Revenue": 120},
        {"Quarter": "Q2", "Revenue": 140},
        {"Quarter": "Q3", "Revenue": 135}
    ])
    
    print("=== Test 1: Generate Chart ===")
    result = generate_chart_from_table(test_data, "Quarterly revenue growth")
    print(result)
    
    # Test 2: Comparison chart
    comparison = json.dumps([
        {"Product": "iPhone", "Sales": 850},
        {"Product": "Mac", "Sales": 420}
    ])
    
    print("\n=== Test 2: Comparison Chart ===")
    result = create_comparison_chart(comparison, "Product sales comparison")
    print(result)
    
    print("\n✅ Tool tests complete!")
