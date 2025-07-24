import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def quick_map_visualization():
    """Create a simple matplotlib visualization of the optimization results."""
    csv_file = "osrm_fix_schedule_mixed_1.5d_1.0t.csv"
    
    print(f"Loading results from: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # Separate fixed and remaining locations
    fixed_locations = df[df['Status'] == 'TO_FIX'].copy()
    remaining_locations = df[df['Status'] == 'REMAINING'].copy()
    
    print(f"Found {len(fixed_locations)} locations to fix and {len(remaining_locations)} remaining locations")
    
    # Create detailed visualization
    fig = plt.figure(figsize=(20, 16))
    
    # Main overview map
    ax1 = plt.subplot(2, 3, (1, 4))  # Spans multiple cells
    
    # Plot all remaining locations
    scatter1 = ax1.scatter(remaining_locations['Longitude'], remaining_locations['Latitude'], 
                          c='lightblue', s=30, alpha=0.6, label='Remaining Locations')
    
    # Plot locations to fix with priority colors
    if len(fixed_locations) > 0:
        scatter2 = ax1.scatter(fixed_locations['Longitude'], fixed_locations['Latitude'], 
                              c=fixed_locations['Priority'], s=400, cmap='Reds', 
                              edgecolors='black', linewidth=3, label='To Fix (Priority Order)',
                              marker='s')  # Square markers for fix locations
        
        # Add priority numbers as text annotations
        for _, row in fixed_locations.iterrows():
            ax1.annotate(str(int(row['Priority'])), 
                        (row['Longitude'], row['Latitude']), 
                        xytext=(0, 0), textcoords='offset points',
                        fontsize=16, fontweight='bold', color='white',
                        ha='center', va='center')
    
    ax1.set_xlabel('Longitude', fontsize=14)
    ax1.set_ylabel('Latitude', fontsize=14)
    ax1.set_title('Water Meter Fix Schedule - Mixed Optimization (1.5x Distance + 1.0x Time)', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Detailed view of fix locations
    ax2 = plt.subplot(2, 3, 2)
    if len(fixed_locations) > 0:
        fix_lats = fixed_locations['Latitude'].values
        fix_lons = fixed_locations['Longitude'].values
        
        # Add margin around fix locations
        lat_margin = max((fix_lats.max() - fix_lats.min()) * 0.2, 0.005)
        lon_margin = max((fix_lons.max() - fix_lons.min()) * 0.2, 0.005)
        
        # Show nearby remaining locations
        nearby_mask = (
            (remaining_locations['Latitude'] >= fix_lats.min() - lat_margin) &
            (remaining_locations['Latitude'] <= fix_lats.max() + lat_margin) &
            (remaining_locations['Longitude'] >= fix_lons.min() - lon_margin) &
            (remaining_locations['Longitude'] <= fix_lons.max() + lon_margin)
        )
        nearby_remaining = remaining_locations[nearby_mask]
        
        ax2.scatter(nearby_remaining['Longitude'], nearby_remaining['Latitude'], 
                   c='lightblue', s=60, alpha=0.7, label='Nearby Remaining')
        
        scatter3 = ax2.scatter(fixed_locations['Longitude'], fixed_locations['Latitude'], 
                              c=fixed_locations['Priority'], s=500, cmap='Reds', 
                              edgecolors='black', linewidth=3, label='To Fix',
                              marker='s')
        
        # Add priority numbers
        for _, row in fixed_locations.iterrows():
            ax2.annotate(str(int(row['Priority'])), 
                        (row['Longitude'], row['Latitude']), 
                        xytext=(0, 0), textcoords='offset points',
                        fontsize=18, fontweight='bold', color='white',
                        ha='center', va='center')
        
        ax2.set_xlim(fix_lons.min() - lon_margin, fix_lons.max() + lon_margin)
        ax2.set_ylim(fix_lats.min() - lat_margin, fix_lats.max() + lat_margin)
        
        ax2.set_xlabel('Longitude', fontsize=12)
        ax2.set_ylabel('Latitude', fontsize=12)
        ax2.set_title('Detailed View: Fix Locations', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No locations to fix', ha='center', va='center', transform=ax2.transAxes)
    
    # Priority details
    ax3 = plt.subplot(2, 3, 3)
    ax3.axis('off')
    
    details_text = "🔧 LOCATIONS TO FIX\n(Priority Order)\n\n"
    if len(fixed_locations) > 0:
        for _, row in fixed_locations.iterrows():
            details_text += f"Priority {int(row['Priority'])}:\n"
            details_text += f"  Location {row['LocationIndex']}\n"
            details_text += f"  {row['Latitude']:.6f}, {row['Longitude']:.6f}\n\n"
    else:
        details_text += "No locations scheduled for fixing"
    
    ax3.text(0.05, 0.95, details_text, transform=ax3.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8))
    
    # Statistics panel
    ax4 = plt.subplot(2, 3, 5)
    ax4.axis('off')
    
    stats_text = f"""📊 OPTIMIZATION SUMMARY
    
Optimization Method: Mixed
• Distance Weight: 1.5x
• Time Weight: 1.0x

Results:
• Total Locations: {len(df)}
• To Fix: {len(fixed_locations)}
• Remaining: {len(remaining_locations)}

Geographic Coverage:
• Lat Range: {df['Latitude'].min():.6f} to {df['Latitude'].max():.6f}
• Lon Range: {df['Longitude'].min():.6f} to {df['Longitude'].max():.6f}
• Area Span: {(df['Latitude'].max()-df['Latitude'].min()):.6f}° × {(df['Longitude'].max()-df['Longitude'].min()):.6f}°
"""
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
    
    # Distance distribution
    ax5 = plt.subplot(2, 3, 6)
    if len(fixed_locations) > 1:
        # Calculate distances between consecutive priority locations
        sorted_fixes = fixed_locations.sort_values('Priority')
        distances = []
        for i in range(len(sorted_fixes) - 1):
            lat1, lon1 = sorted_fixes.iloc[i][['Latitude', 'Longitude']]
            lat2, lon2 = sorted_fixes.iloc[i+1][['Latitude', 'Longitude']]
            # Simple distance calculation (not geodesic, but good for visualization)
            dist = np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111.32  # Rough km conversion
            distances.append(dist)
        
        priorities = list(range(1, len(distances) + 1))
        bars = ax5.bar(priorities, distances, color='skyblue', edgecolor='navy', linewidth=2)
        ax5.set_xlabel('Priority Transition', fontsize=12)
        ax5.set_ylabel('Distance (km)', fontsize=12)
        ax5.set_title('Distance Between Sequential Fixes', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, dist in zip(bars, distances):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{dist:.2f}', ha='center', va='bottom', fontweight='bold')
    else:
        ax5.text(0.5, 0.5, 'Need 2+ locations\nto show distances', 
                ha='center', va='center', transform=ax5.transAxes, fontsize=12)
        ax5.set_title('Distance Analysis', fontsize=12)
    
    plt.tight_layout(pad=3.0)
    
    # Save the visualization
    os.makedirs("visualizations", exist_ok=True)
    output_file = "visualizations/water_meters_map.png"
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print(f"\n✅ Visualization saved to: {output_file}")
    print(f"📍 Map shows {len(fixed_locations)} priority locations to fix")
    print(f"🔵 {len(remaining_locations)} remaining locations shown in blue")
    
    # Show the plot
    plt.show()
    
    # Print priority summary
    print(f"\n🔧 FIX SCHEDULE SUMMARY:")
    if len(fixed_locations) > 0:
        for _, row in fixed_locations.iterrows():
            print(f"  Priority {int(row['Priority'])}: Location {row['LocationIndex']} at ({row['Latitude']:.6f}, {row['Longitude']:.6f})")
    else:
        print("  No locations currently scheduled for fixing")

if __name__ == "__main__":
    quick_map_visualization()
