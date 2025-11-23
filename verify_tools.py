"""
IBM Watsonx Orchestrate Tool Registration Helper

This script helps verify that all tools are properly decorated and ready
for registration in IBM Watsonx Orchestrate.

Usage:
    python verify_tools.py
"""

import sys
import importlib.util
from pathlib import Path


def load_module_from_file(file_path: Path):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"❌ Error loading {file_path.name}: {e}")
        return None


def find_tool_functions(module):
    """Find all @tool decorated functions in a module"""
    tools = []
    
    if not module:
        return tools
    
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and hasattr(obj, '__wrapped__'):
            # Check if it's likely a @tool decorated function
            tools.append({
                'name': name,
                'doc': obj.__doc__ or 'No description',
                'module': module.__name__
            })
    
    return tools


def verify_all_tools():
    """Verify all tool files are ready for Watsonx Orchestrate"""
    
    print("=" * 80)
    print("IBM WATSONX ORCHESTRATE - TOOL VERIFICATION")
    print("=" * 80)
    print()
    
    workspace = Path(__file__).parent
    tools_dir = workspace / "tools"
    
    tool_files = [
        "risk_scorer_tool.py",
        "chart_generator_tool.py",
        "feed_poster_tool.py"
    ]
    
    all_tools = []
    total_tools = 0
    
    for tool_file in tool_files:
        tool_path = tools_dir / tool_file
        
        print(f"📁 Checking: {tool_file}")
        print("-" * 80)
        
        if not tool_path.exists():
            print(f"❌ File not found: {tool_path}")
            print()
            continue
        
        # Load module
        module = load_module_from_file(tool_path)
        
        if not module:
            print()
            continue
        
        # Find tools
        tools = find_tool_functions(module)
        
        if tools:
            print(f"✅ Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"   • {tool['name']}")
                # Print first line of docstring
                first_line = tool['doc'].strip().split('\n')[0]
                print(f"     └─ {first_line}")
            total_tools += len(tools)
            all_tools.extend(tools)
        else:
            print("⚠️  No @tool decorated functions found")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tool files checked: {len(tool_files)}")
    print(f"Total tools found: {total_tools}")
    print()
    
    if total_tools > 0:
        print("✅ All tools are ready for registration!")
        print()
        print("Expected tool count by agent:")
        print("  • Risk Scorer Agent: 4 tools")
        print("  • Chart Generator Agent: 5 tools")
        print("  • Feed Poster Agent: 4 tools")
        print(f"  • Total: 13 tools (Found: {total_tools})")
        print()
        
        if total_tools == 13:
            print("🎉 Perfect! All 13 tools detected and ready!")
        else:
            print(f"⚠️  Expected 13 tools, found {total_tools}")
    else:
        print("❌ No tools found. Check @tool decorators.")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Upload agent YAML files to IBM Watsonx Orchestrate")
    print("2. Register tool files (risk_scorer_tool.py, etc.)")
    print("3. Configure flow connections")
    print("4. Test the complete pipeline")
    print()
    print("See WATSONX_ORCHESTRATE_DEPLOYMENT.md for detailed instructions.")
    print("=" * 80)


if __name__ == "__main__":
    verify_all_tools()
