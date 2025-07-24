import pandas as pd
import folium
import matplotlib.pyplot as plt
import numpy as np
import webbrowser
import os

# Quick visualization of your current results
def visualize_current_results():
    """Quickly visualize the current OSRM results."""
    csv_file = "osrm_fix_schedule_mixed_1.5d_1.0t.csv"
    
    print(f"Loading results from: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # Separate fixed and remaining locations
    fixed_locations = df[df['Status'] == 'TO_FIX'].copy()
    remaining_locations = df[df['Status'] == 'REMAINING'].copy()
    
    print(f"Found {len(fixed_locations)} locations to fix and {len(remaining_locations)} remaining locations")
    
    # Calculate center point
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    
    # Create satellite map
    print("Creating satellite map...")
    satellite_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=None
    )
    
    # Add satellite tile layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(satellite_map)
    
    # Add locations to fix (red markers with priority numbers)
    for _, row in fixed_locations.iterrows():
        priority = int(row['Priority'])
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>TO FIX - Priority {priority}</b><br>"
                  f"Location {row['LocationIndex']}<br>"
                  f"Lat: {row['Latitude']:.6f}<br>"
                  f"Lon: {row['Longitude']:.6f}",
            tooltip=f"Fix Priority {priority}",
            icon=folium.Icon(color='red', icon='exclamation-sign', icon_size=(30, 30))
        ).add_to(satellite_map)
        
        # Add priority number as a label
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=f'<div style="background-color: white; border: 2px solid red; border-radius: 50%; width: 30px; height: 30px; text-align: center; line-height: 26px; font-weight: bold; font-size: 14px; color: red;">{priority}</div>',
                icon_size=(30, 30),
                icon_anchor=(15, 15)
            )
        ).add_to(satellite_map)
    
    # Add remaining locations (blue circles)
    for _, row in remaining_locations.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=f"<b>REMAINING</b><br>"
                  f"Location {row['LocationIndex']}<br>"
                  f"Lat: {row['Latitude']:.6f}<br>"
                  f"Lon: {row['Longitude']:.6f}",
            tooltip=f"Remaining Location {row['LocationIndex']}",
            color='blue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.7,
            weight=2
        ).add_to(satellite_map)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;">
    <h4 style="margin-top: 0;">Water Meter Fix Schedule</h4>
    <p><span style="color:red; font-size:16px;">🔴</span> Locations to Fix (Priority Order)</p>
    <p><span style="color:blue; font-size:16px;">🔵</span> Remaining Locations</p>
    <p><small>Optimization: Mixed (1.5x Distance + 1.0x Time)</small></p>
    <p><small>Total: 3 to fix, 237 remaining</small></p>
    </div>
    """
    satellite_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Create street map
    print("Creating street map...")
    street_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add same markers to street map
    for _, row in fixed_locations.iterrows():
        priority = int(row['Priority'])
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>TO FIX - Priority {priority}</b><br>"
                  f"Location {row['LocationIndex']}<br>"
                  f"Lat: {row['Latitude']:.6f}<br>"
                  f"Lon: {row['Longitude']:.6f}",
            tooltip=f"Fix Priority {priority}",
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(street_map)
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=f'<div style="background-color: white; border: 2px solid red; border-radius: 50%; width: 30px; height: 30px; text-align: center; line-height: 26px; font-weight: bold; font-size: 14px; color: red;">{priority}</div>',
                icon_size=(30, 30),
                icon_anchor=(15, 15)
            )
        ).add_to(street_map)
    
    for _, row in remaining_locations.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=f"<b>REMAINING</b><br>"
                  f"Location {row['LocationIndex']}<br>"
                  f"Lat: {row['Latitude']:.6f}<br>"
                  f"Lon: {row['Longitude']:.6f}",
            tooltip=f"Remaining Location {row['LocationIndex']}",
            color='blue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.7,
            weight=2
        ).add_to(street_map)
    
    street_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Save maps
    os.makedirs("visualizations", exist_ok=True)
    satellite_file = "visualizations/water_meters_satellite.html"
    street_file = "visualizations/water_meters_street.html"
    
    satellite_map.save(satellite_file)
    street_map.save(street_file)
    
    # Create overview plot
    print("Creating overview plot...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: All locations with fix priorities
    ax1.scatter(remaining_locations['Longitude'], remaining_locations['Latitude'], 
               c='lightblue', s=30, alpha=0.7, label='Remaining Locations')
    
    scatter = ax1.scatter(fixed_locations['Longitude'], fixed_locations['Latitude'], 
                         c=fixed_locations['Priority'], s=200, cmap='Reds', 
                         edgecolors='black', linewidth=2, label='To Fix (Priority)')
    
    # Add priority numbers
    for _, row in fixed_locations.iterrows():
        ax1.annotate(str(int(row['Priority'])), 
                    (row['Longitude'], row['Latitude']), 
                    xytext=(0, 0), textcoords='offset points',
                    fontsize=12, fontweight='bold', color='white',
                    ha='center', va='center')
    
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title('Water Meter Locations - Fix Schedule Overview')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Zoomed view of fix locations
    if len(fixed_locations) > 0:
        fix_lats = fixed_locations['Latitude'].values
        fix_lons = fixed_locations['Longitude'].values
        
        # Add some padding around fix locations
        lat_margin = (fix_lats.max() - fix_lats.min()) * 0.1 or 0.01
        lon_margin = (fix_lons.max() - fix_lons.min()) * 0.1 or 0.01
        
        ax2.set_xlim(fix_lons.min() - lon_margin, fix_lons.max() + lon_margin)
        ax2.set_ylim(fix_lats.min() - lat_margin, fix_lats.max() + lat_margin)
        
        # Show nearby remaining locations too
        nearby_mask = (
            (remaining_locations['Latitude'] >= fix_lats.min() - lat_margin) &
            (remaining_locations['Latitude'] <= fix_lats.max() + lat_margin) &
            (remaining_locations['Longitude'] >= fix_lons.min() - lon_margin) &
            (remaining_locations['Longitude'] <= fix_lons.max() + lon_margin)
        )
        nearby_remaining = remaining_locations[nearby_mask]
        
        ax2.scatter(nearby_remaining['Longitude'], nearby_remaining['Latitude'], 
                   c='lightblue', s=40, alpha=0.7, label='Nearby Remaining')
        
        scatter2 = ax2.scatter(fixed_locations['Longitude'], fixed_locations['Latitude'], 
                              c=fixed_locations['Priority'], s=300, cmap='Reds', 
                              edgecolors='black', linewidth=2, label='To Fix')
        
        for _, row in fixed_locations.iterrows():
            ax2.annotate(str(int(row['Priority'])), 
                        (row['Longitude'], row['Latitude']), 
                        xytext=(0, 0), textcoords='offset points',
                        fontsize=14, fontweight='bold', color='white',
                        ha='center', va='center')
        
        ax2.set_xlabel('Longitude')
        ax2.set_ylabel('Latitude')
        ax2.set_title('Detailed View: Locations to Fix')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Location details
    ax3.axis('off')
    details_text = "LOCATIONS TO FIX (Priority Order):\n\n"
    for _, row in fixed_locations.iterrows():
        details_text += f"Priority {int(row['Priority'])}: Location {row['LocationIndex']}\n"
        details_text += f"  Lat: {row['Latitude']:.6f}\n"
        details_text += f"  Lon: {row['Longitude']:.6f}\n\n"
    
    ax3.text(0.05, 0.95, details_text, transform=ax3.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    # Plot 4: Statistics
    ax4.axis('off')
    stats_text = f"""
    OPTIMIZATION RESULTS SUMMARY
    
    Optimization Method: Mixed
    Distance Weight: 1.5
    Time Weight: 1.0
    
    Total Locations: {len(df)}
    Locations to Fix: {len(fixed_locations)}
    Remaining Locations: {len(remaining_locations)}
    
    Geographic Bounds:
    Latitude: {df['Latitude'].min():.6f} to {df['Latitude'].max():.6f}
    Longitude: {df['Longitude'].min():.6f} to {df['Longitude'].max():.6f}
    
    Results saved to:
    • {satellite_file}
    • {street_file}
    """
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save overview plot
    overview_file = "visualizations/water_meters_overview.png"
    fig.savefig(overview_file, dpi=300, bbox_inches='tight')
    
    print(f"\nVisualizations created:")
    print(f"  • Satellite map: {satellite_file}")
    print(f"  • Street map: {street_file}")
    print(f"  • Overview plot: {overview_file}")
    
    # Open maps in browser
    try:
        print(f"\nOpening maps in browser...")
        webbrowser.open(f'file://{os.path.abspath(satellite_file)}')
        webbrowser.open(f'file://{os.path.abspath(street_file)}')
        print("Maps opened successfully!")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Please manually open: {os.path.abspath(satellite_file)}")
    
    # Show matplotlib plot
    plt.show()

if __name__ == "__main__":
    visualize_current_results()
