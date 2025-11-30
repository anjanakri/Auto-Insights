import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd

class VisualizationTool:
    """Tool for generating visualizations from dataframes"""
    
    @staticmethod
    def create_chart(df: pd.DataFrame, chart_type: str = 'bar') -> str:
        """Generate chart and return as base64 string"""
        plt.figure(figsize=(12, 6))
        plt.style.use('seaborn-v0_8-darkgrid')
        
        if chart_type == 'line' and len(df) > 2:
            for column in df.columns[1:]:
                plt.plot(df.iloc[:, 0], df[column], marker='o', 
                        linewidth=2, markersize=8, label=column)
            plt.xlabel(df.columns[0], fontsize=12)
            plt.ylabel('Values', fontsize=12)
            plt.legend(fontsize=10)
            plt.grid(True, alpha=0.3)
            
        elif chart_type == 'bar':
            df_plot = df.head(10)
            x_pos = range(len(df_plot))
            
            if len(df.columns) == 2:
                plt.bar(x_pos, df_plot.iloc[:, 1], color='#4285F4', alpha=0.8)
                plt.xlabel(df.columns[0], fontsize=12)
                plt.ylabel(df.columns[1], fontsize=12)
                plt.xticks(x_pos, df_plot.iloc[:, 0], rotation=45, ha='right')
            else:
                df_plot.plot(x=df.columns[0], kind='bar', ax=plt.gca(), 
                           color=['#4285F4', '#34A853', '#FBBC04'])
        
        plt.title('Data Analysis Visualization', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
