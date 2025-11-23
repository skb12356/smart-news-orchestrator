"""
Chart Generation Tool for IBM Watsonx Orchestrate
Analyzes tabular data and generates appropriate visualizations using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Union
import re

class ChartGenerator:
    """
    Analyzes tabular data and generates appropriate charts.
    Saves charts locally and returns metadata for embedding in articles.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the chart generator.
        
        Args:
            output_dir: Directory to save generated charts (default: agents/charts/)
        """
        if output_dir is None:
            # Default to hackathon-IBM/agents/charts/
            base_path = Path(__file__).resolve().parents[1]
            output_dir = base_path / "agents" / "charts"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, chart_type: str, article_id: str = None, chart_number: int = None) -> str:
        """Generate unique filename for chart."""
        if article_id and chart_number:
            return f"{article_id}_{chart_number}.png"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"chart_{chart_type}_{timestamp}.png"
    
    def _detect_chart_type(self, data: List[Dict[str, Any]], instruction: str = "") -> str:
        """
        Analyze data structure and decide the best chart type.
        
        Args:
            data: List of dictionaries representing tabular data
            instruction: Context about what the data represents
            
        Returns:
            Chart type: line, bar, pie, heatmap, histogram, etc.
        """
        if not data or len(data) == 0:
            return "bar"  # Default fallback
        
        # Get column names and types
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Detect numeric columns
        numeric_cols = []
        categorical_cols = []
        date_cols = []
        
        for col in columns:
            sample_values = [row.get(col) for row in data[:5] if row.get(col) is not None]
            if not sample_values:
                continue
            
            # Check if date/time
            if any(kw in col.lower() for kw in ['date', 'time', 'quarter', 'month', 'year', 'week']):
                date_cols.append(col)
            # Check if numeric
            elif all(isinstance(v, (int, float)) for v in sample_values):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        
        # Decision logic
        instruction_lower = instruction.lower()
        
        # Time series data
        if date_cols and numeric_cols:
            if 'trend' in instruction_lower or 'growth' in instruction_lower or 'over time' in instruction_lower:
                return "line"
            return "line"
        
        # Composition/percentage data
        if 'percentage' in instruction_lower or 'composition' in instruction_lower or 'share' in instruction_lower:
            return "pie"
        
        # Comparative data
        if categorical_cols and numeric_cols:
            if len(data) <= 10:  # Small number of categories
                return "bar"
            else:
                return "bar"
        
        # Multiple numeric columns (correlation)
        if len(numeric_cols) >= 2 and len(data) > 5:
            return "line"  # Multi-line chart
        
        # Distribution data
        if 'distribution' in instruction_lower or 'histogram' in instruction_lower:
            return "histogram"
        
        # Default to bar chart
        return "bar"
    
    def _create_line_chart(self, data: List[Dict[str, Any]], instruction: str, article_id: str = None, chart_number: int = None) -> str:
        """Create a line chart."""
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Find x-axis (date/categorical) and y-axis (numeric)
        x_col = columns[0]
        y_cols = []
        
        for col in columns[1:]:
            sample_val = data[0].get(col)
            if isinstance(sample_val, (int, float)):
                y_cols.append(col)
        
        if not y_cols:
            y_cols = [columns[1]]
        
        # Extract data
        x_values = [row[x_col] for row in data]
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        for y_col in y_cols:
            y_values = [row.get(y_col, 0) for row in data]
            plt.plot(x_values, y_values, marker='o', label=y_col, linewidth=2)
        
        plt.title(instruction or "Line Chart", fontsize=14, fontweight='bold')
        plt.xlabel(x_col, fontsize=11)
        plt.ylabel(y_cols[0] if len(y_cols) == 1 else "Values", fontsize=11)
        
        if len(y_cols) > 1:
            plt.legend()
        
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save
        filename = self._generate_filename("line", article_id, chart_number)
        output_path = self.output_dir / filename
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        
        return str(output_path)
    
    def _create_bar_chart(self, data: List[Dict[str, Any]], instruction: str, article_id: str = None, chart_number: int = None) -> str:
        """Create a bar chart."""
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Find categorical and numeric columns
        x_col = columns[0]
        y_col = columns[1]
        
        for col in columns[1:]:
            sample_val = data[0].get(col)
            if isinstance(sample_val, (int, float)):
                y_col = col
                break
        
        # Extract data
        x_values = [str(row[x_col]) for row in data]
        y_values = [row.get(y_col, 0) for row in data]
        
        # Create plot
        plt.figure(figsize=(10, 6))
        bars = plt.bar(x_values, y_values, edgecolor='black', alpha=0.7)
        
        # Color gradient
        colors = plt.cm.viridis([i/len(bars) for i in range(len(bars))])
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        plt.title(instruction or "Bar Chart", fontsize=14, fontweight='bold')
        plt.xlabel(x_col, fontsize=11)
        plt.ylabel(y_col, fontsize=11)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Save
        filename = self._generate_filename("bar", article_id, chart_number)
        output_path = self.output_dir / filename
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        
        return str(output_path)
    
    def _create_pie_chart(self, data: List[Dict[str, Any]], instruction: str, article_id: str = None, chart_number: int = None) -> str:
        """Create a pie chart."""
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Find label and value columns
        label_col = columns[0]
        value_col = columns[1]
        
        for col in columns[1:]:
            sample_val = data[0].get(col)
            if isinstance(sample_val, (int, float)):
                value_col = col
                break
        
        # Extract data
        labels = [str(row[label_col]) for row in data]
        values = [row.get(value_col, 0) for row in data]
        
        # Create plot
        plt.figure(figsize=(10, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(instruction or "Pie Chart", fontsize=14, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        
        # Save
        filename = self._generate_filename("pie", article_id, chart_number)
        output_path = self.output_dir / filename
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        
        return str(output_path)
    
    def _create_histogram(self, data: List[Dict[str, Any]], instruction: str, article_id: str = None, chart_number: int = None) -> str:
        """Create a histogram."""
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Find numeric column
        value_col = columns[0]
        for col in columns:
            sample_val = data[0].get(col)
            if isinstance(sample_val, (int, float)):
                value_col = col
                break
        
        # Extract data
        values = [row.get(value_col, 0) for row in data]
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=20, edgecolor='black', alpha=0.7)
        plt.title(instruction or "Histogram", fontsize=14, fontweight='bold')
        plt.xlabel(value_col, fontsize=11)
        plt.ylabel("Frequency", fontsize=11)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Save
        filename = self._generate_filename("histogram", article_id, chart_number)
        output_path = self.output_dir / filename
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        
        return str(output_path)
    
    def generate_chart(self, 
                      data: Union[List[Dict[str, Any]], str], 
                      instruction: str = "",
                      chart_type: str = "auto",
                      article_id: str = None,
                      chart_number: int = None) -> Dict[str, Any]:
        """
        Main entry point: Generate a chart from tabular data.
        
        Args:
            data: List of dicts OR JSON string representing tabular data
            instruction: Natural language context about the data
            chart_type: Specific chart type or "auto" to auto-detect
            article_id: Article identifier (e.g., "article1", "article2")
            chart_number: Chart number within article (e.g., 1, 2, 3)
            
        Returns:
            Dictionary with:
                - chart_type: Type of chart generated
                - file_path: Local path to saved PNG
                - description: Insight description
        """
        try:
            # Parse input if JSON string
            if isinstance(data, str):
                data = json.loads(data)
            
            # Validate data
            if not data or not isinstance(data, list) or len(data) == 0:
                return {
                    "error": "Invalid or empty dataset provided.",
                    "details": "Data must be a non-empty list of dictionaries"
                }
            
            # Auto-detect chart type if needed
            if chart_type == "auto":
                chart_type = self._detect_chart_type(data, instruction)
            
            # Generate chart based on type
            if chart_type == "line":
                file_path = self._create_line_chart(data, instruction, article_id, chart_number)
                description = f"Line chart showing trends in {instruction or 'the data'}"
            elif chart_type == "bar":
                file_path = self._create_bar_chart(data, instruction, article_id, chart_number)
                description = f"Bar chart comparing {instruction or 'categories'}"
            elif chart_type == "pie":
                file_path = self._create_pie_chart(data, instruction, article_id, chart_number)
                description = f"Pie chart showing composition of {instruction or 'the data'}"
            elif chart_type == "histogram":
                file_path = self._create_histogram(data, instruction, article_id, chart_number)
                description = f"Histogram showing distribution of {instruction or 'values'}"
            else:
                # Default to bar chart
                file_path = self._create_bar_chart(data, instruction, article_id, chart_number)
                description = f"Chart visualizing {instruction or 'the data'}"
            
            return {
                "chart_type": chart_type,
                "file_path": file_path,
                "description": description
            }
            
        except Exception as e:
            return {
                "error": "Failed to generate chart",
                "details": str(e)
            }


# Standalone test function
def main():
    """Test the chart generator with sample data."""
    generator = ChartGenerator()
    
    # Test 1: Line chart (time series)
    print("\n=== Test 1: Line Chart ===")
    quarterly_data = [
        {"Quarter": "Q1", "Revenue": 120},
        {"Quarter": "Q2", "Revenue": 140},
        {"Quarter": "Q3", "Revenue": 135},
        {"Quarter": "Q4", "Revenue": 150}
    ]
    result = generator.generate_chart(
        quarterly_data, 
        "Quarterly revenue growth for NovaTech"
    )
    print(json.dumps(result, indent=2))
    
    # Test 2: Bar chart (categorical comparison)
    print("\n=== Test 2: Bar Chart ===")
    category_data = [
        {"Product": "iPhone", "Sales": 850},
        {"Product": "Mac", "Sales": 420},
        {"Product": "iPad", "Sales": 310},
        {"Product": "Wearables", "Sales": 280}
    ]
    result = generator.generate_chart(
        category_data,
        "Product sales comparison",
        chart_type="bar"
    )
    print(json.dumps(result, indent=2))
    
    # Test 3: Pie chart (composition)
    print("\n=== Test 3: Pie Chart ===")
    market_share = [
        {"Company": "Apple", "Share": 35},
        {"Company": "Samsung", "Share": 28},
        {"Company": "Huawei", "Share": 15},
        {"Company": "Others", "Share": 22}
    ]
    result = generator.generate_chart(
        market_share,
        "Global smartphone market share",
        chart_type="pie"
    )
    print(json.dumps(result, indent=2))
    
    print("\n✅ All charts generated successfully!")
    print(f"📁 Charts saved to: {generator.output_dir}")


if __name__ == "__main__":
    main()
