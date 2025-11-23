import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import numpy as np

# Set the style
plt.style.use('default')

# Load the JSON data
json_path = r'C:\Users\saksh\OneDrive\Desktop\Projects\IBM-ORCHESTRA\hackathon-IBM\agents\risk_agent\risk_assessment_results.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data.get('detailed_results', [])

print(f"📊 Found {len(articles)} articles to process")

output_dir = r'C:\Users\saksh\OneDrive\Desktop\Projects\IBM-ORCHESTRA\hackathon-IBM\dashboard\public\agents\charts'
os.makedirs(output_dir, exist_ok=True)

def get_risk_color(risk_score):
    """Return color based on risk score"""
    if risk_score >= 0.7:
        return '#ef4444'  # red
    elif risk_score >= 0.4:
        return '#f59e0b'  # amber/yellow
    else:
        return '#10b981'  # green

def get_sentiment_color(sentiment):
    """Return color based on sentiment"""
    if sentiment.lower() == 'positive':
        return '#10b981'  # green
    elif sentiment.lower() == 'negative':
        return '#ef4444'  # red
    else:
        return '#6b7280'  # gray

# Generate charts for each article using sequential numbering
chart_count = 0

for idx, article in enumerate(articles, 1):
    try:
        # Use sequential index (1-22) instead of the article_index from JSON
        article_num = idx
        title = article.get('title', 'Untitled')[:50]
        
        risk_analysis = article.get('risk_analysis', {})
        risk_score = risk_analysis.get('risk_score', 0)
        sentiment_label = risk_analysis.get('sentiment_label', 'neutral')
        sentiment_score = risk_analysis.get('sentiment_score', 0)
        risk_categories = risk_analysis.get('risk_category', [])
        
        print(f"  Generating charts for Article #{article_num}: {title}")
        
        # Chart 1: Risk Score Gauge
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        
        # Create horizontal bar for risk score
        risk_percentage = risk_score * 100
        risk_color = get_risk_color(risk_score)
        
        ax.barh([0], [risk_percentage], height=0.5, color=risk_color, alpha=0.8)
        ax.barh([0], [100], height=0.5, color='#2d2d44', alpha=0.3, zorder=0)
        
        # Add percentage text
        ax.text(risk_percentage/2, 0, f'{risk_percentage:.1f}%', 
                ha='center', va='center', fontsize=24, fontweight='bold', color='white')
        
        # Styling
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'], color='white', fontsize=10)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        
        risk_level = 'HIGH' if risk_score >= 0.7 else 'MEDIUM' if risk_score >= 0.4 else 'LOW'
        ax.set_title(f'Risk Score: {risk_level}', color='white', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart1_path = os.path.join(output_dir, f'article{article_num}_1.png')
        plt.savefig(chart1_path, facecolor='#1a1a2e', dpi=100, bbox_inches='tight')
        plt.close()
        chart_count += 1
        
        # Chart 2: Sentiment and Categories
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='#1a1a2e')
        
        # Left: Sentiment
        ax1.set_facecolor('#1a1a2e')
        sentiment_percentage = sentiment_score * 100
        sentiment_color = get_sentiment_color(sentiment_label)
        
        ax1.barh([sentiment_label.capitalize()], [sentiment_percentage], 
                color=sentiment_color, alpha=0.8, height=0.5)
        ax1.barh([sentiment_label.capitalize()], [100], 
                color='#2d2d44', alpha=0.3, height=0.5, zorder=0)
        
        ax1.text(sentiment_percentage/2, 0, f'{sentiment_percentage:.1f}%', 
                ha='center', va='center', fontsize=16, fontweight='bold', color='white')
        
        ax1.set_xlim(0, 100)
        ax1.set_xticks([0, 50, 100])
        ax1.set_xticklabels(['0%', '50%', '100%'], color='white', fontsize=9)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_color('white')
        ax1.tick_params(axis='both', colors='white')
        ax1.set_title('Sentiment Analysis', color='white', fontsize=14, fontweight='bold', pad=15)
        
        # Right: Top Risk Categories
        ax2.set_facecolor('#1a1a2e')
        
        if risk_categories and len(risk_categories) > 0:
            # Take top 5 categories
            top_categories = risk_categories[:5]
            category_names = [cat.capitalize() for cat in top_categories]
            category_values = [1] * len(top_categories)  # Equal values since we don't have individual scores
            
            colors_palette = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6']
            bar_colors = colors_palette[:len(category_names)]
            
            y_pos = np.arange(len(category_names))
            ax2.barh(y_pos, category_values, color=bar_colors, alpha=0.8)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(category_names, color='white', fontsize=10)
            ax2.set_xticks([])
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.tick_params(axis='y', colors='white')
            ax2.set_title('Top Risk Categories', color='white', fontsize=14, fontweight='bold', pad=15)
        else:
            ax2.text(0.5, 0.5, 'No categories', ha='center', va='center', 
                    color='white', fontsize=12, transform=ax2.transAxes)
            ax2.set_xticks([])
            ax2.set_yticks([])
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.set_title('Top Risk Categories', color='white', fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        chart2_path = os.path.join(output_dir, f'article{article_num}_2.png')
        plt.savefig(chart2_path, facecolor='#1a1a2e', dpi=100, bbox_inches='tight')
        plt.close()
        chart_count += 1
        
    except Exception as e:
        print(f"  ❌ Error processing Article #{article_num}: {str(e)}")
        continue

print(f"\n✅ Successfully generated {chart_count} charts for {len(articles)} articles!")
print(f"📁 Charts saved to: {output_dir}")
