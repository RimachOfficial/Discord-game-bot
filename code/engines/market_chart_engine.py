import os
import re  
import math 
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime

def generate_and_save_market_chart(db_manager) -> str:
    """
    Reads database tables to generate a macro trend stock chart dashboard
    that auto-scales dynamically based on the total number of active tiers.
    """
    prices = dict(db_manager.get_market_prices())
    if not prices:
        return ""

    plt.style.use('dark_background')
    
    # Grab all available tiers dynamically (No slices, no hardcoding!)
    tracked_tiers = list(prices.keys())
    total_tiers = len(tracked_tiers)
    
    # 📐 CALCULATE OPTIMAL GRID DYNAMICALLY
    # We want roughly a 16:9 ratio grid layout depending on the tier count
    if total_tiers <= 3:
        ncols = total_tiers
        nrows = 1
    elif total_tiers <= 6:
        ncols = 3
        nrows = math.ceil(total_tiers / ncols)
    else:
        ncols = 4 if total_tiers in [4, 8] else 5  # Favor neat 4 or 5 col layouts
        nrows = math.ceil(total_tiers / ncols)
        
    # Auto-scale the canvas window size so charts always have perfect breathing room
    fig_width = max(12, ncols * 4)
    fig_height = max(5, nrows * 3.8)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_width, fig_height))
    
    # If there is only 1 subplot total, wrap it in a list so .flatten() or loop iteration doesn't crash
    if total_tiers == 1:
        axes = [axes]
    else:
        axes = axes.flatten() 

    for idx, tier in enumerate(tracked_tiers):
        ax = axes[idx]
        
        db_manager.cursor.execute("""
            SELECT timestamp, price FROM market_history 
            WHERE tier_name = ? 
            ORDER BY timestamp DESC LIMIT 30
        """, (tier,))
        history = db_manager.cursor.fetchall()
        
        history = history[::-1]
        
        # 🧹 Clean text for font safety
        clean_tier_name = re.sub(r'[^\x00-\x7F]+', '', tier).strip()

        if len(history) < 2:
            ax.text(0.5, 0.5, "Warming up...", ha='center', va='center', alpha=0.4)
            ax.set_title(clean_tier_name, fontsize=10, fontweight='bold')
            continue
            
        timestamps = [datetime.fromtimestamp(row[0]) for row in history]
        price_points = [row[1] for row in history]
        
        current_price = price_points[-1]
        starting_price = price_points[0]
        
        line_color = "#2ecc71" if current_price >= starting_price else "#e74c3c"
        
        ax.plot(timestamps, price_points, color=line_color, linewidth=2)
        ax.fill_between(timestamps, price_points, min(price_points) * 0.98, color=line_color, alpha=0.1)
        
        ax.set_title(clean_tier_name, fontsize=11, fontweight='bold', pad=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Auto-adjust X-axis label spacing depending on layout column density
        ax.xaxis.set_major_locator(ticker.MaxNLocator(3 if ncols >= 4 else 4))
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, linestyle=":", alpha=0.15)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}" if x < 1e6 else f"${x:.1e}"))

    # 🧹 DYNAMIC CLEANUP: Automatically hides any empty subplot squares left at the end
    for jdx in range(len(tracked_tiers), len(axes)):
        fig.delaxes(axes[jdx])

    plt.suptitle("Live Stock Market Macro Trends", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = os.path.join(os.getcwd(), "market_trend.png")
    plt.savefig(output_path, format='png', dpi=120)
    plt.close(fig)
    
    return output_path