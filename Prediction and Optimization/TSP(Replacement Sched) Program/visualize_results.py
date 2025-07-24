import pandas as pd
import folium
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Tuple, Optional
import webbrowser
import os

class TSPResultVisualizer:
    def __init__(self, csv_file: str):
        """Initialize the visualizer with results from CSV file."""
        self.df = pd.read_csv(csv_file)
        self.csv_file = csv_file
        
        # Separate fixed and remaining locations
        self.fixed_locations = self.df[self.df['Status'] == 'TO_FIX'].copy()
        self.remaining_locations = self.df[self.df['Status'] == 'REMAINING'].copy()
        
        # Get optimization details
        self.optimization_method = self.df['OptimizationMethod'].iloc[0]
        if self.optimization_method == 'mixed':
            self.distance_weight = self.df['DistanceWeight'].iloc[0]
            self.time_weight = self.df['TimeWeight'].iloc[0]
        
        print(f"Loaded {len(self.fixed_locations)} locations to fix and {len(self.remaining_locations)} remaining locations")
        
    def create_folium_map(self, map_type: str = "OpenStreetMap") -> folium.Map:
        """Create an interactive Folium map."""
        # Calculate center point
        all_lats = self.df['Latitude'].values
        all_lons = self.df['Longitude'].values
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # Create map with specified tile layer
        if map_type.lower() == "satellite":
            # Use satellite imagery
            m = folium.Map(
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
            ).add_to(m)
        else:
            # Use standard map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
        
        # Add locations to fix (red markers with priority numbers)
        for _, row in self.fixed_locations.iterrows():
            priority = int(row['Priority'])
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"<b>TO FIX - Priority {priority}</b><br>"
                      f"Location {row['LocationIndex']}<br>"
                      f"Lat: {row['Latitude']:.6f}<br>"
                      f"Lon: {row['Longitude']:.6f}",
                tooltip=f"Fix Priority {priority}",
                icon=folium.Icon(color='red', icon='exclamation-sign')
            ).add_to(m)
            
            # Add priority number as a label
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                icon=folium.DivIcon(
                    html=f'<div style="background-color: white; border: 2px solid red; border-radius: 50%; width: 25px; height: 25px; text-align: center; line-height: 21px; font-weight: bold; font-size: 12px;">{priority}</div>',
                    icon_size=(25, 25),
                    icon_anchor=(12, 12)
                )
            ).add_to(m)
        
        # Add remaining locations (blue markers)
        for _, row in self.remaining_locations.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=4,
                popup=f"<b>REMAINING</b><br>"
                      f"Location {row['LocationIndex']}<br>"
                      f"Lat: {row['Latitude']:.6f}<br>"
                      f"Lon: {row['Longitude']:.6f}",
                tooltip=f"Remaining Location {row['LocationIndex']}",
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.7
            ).add_to(m)
        
        # Add legend
        legend_html = f"""
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Water Meter Fix Schedule</h4>
        <p><i class="fa fa-exclamation-sign" style="color:red"></i> Locations to Fix (Priority Order)</p>
        <p><i class="fa fa-circle" style="color:blue"></i> Remaining Locations</p>
        <p><small>Optimization: {self.optimization_method.title()}</small></p>
        """
        
        if self.optimization_method == 'mixed':
            legend_html += f"<p><small>Weights: {self.distance_weight:.1f}x Distance + {self.time_weight:.1f}x Time</small></p>"
        
        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def create_matplotlib_overview(self) -> plt.Figure:
        """Create a matplotlib overview plot."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: All locations with fix priorities
        ax1.scatter(self.remaining_locations['Longitude'], self.remaining_locations['Latitude'], 
                   c='lightblue', s=30, alpha=0.7, label='Remaining Locations')
        
        scatter = ax1.scatter(self.fixed_locations['Longitude'], self.fixed_locations['Latitude'], 
                             c=self.fixed_locations['Priority'], s=100, cmap='Reds', 
                             edgecolors='black', linewidth=1, label='To Fix (Priority)')
        
        # Add priority numbers
        for _, row in self.fixed_locations.iterrows():
            ax1.annotate(str(int(row['Priority'])), 
                        (row['Longitude'], row['Latitude']), 
                        xytext=(3, 3), textcoords='offset points',
                        fontsize=8, fontweight='bold', color='white')
        
        ax1.set_xlabel('Longitude')
        ax1.set_ylabel('Latitude')
        ax1.set_title('Water Meter Locations - Fix Schedule Overview')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, label='Fix Priority')
        
        # Plot 2: Geographic distribution
        ax2.hist2d(self.df['Longitude'], self.df['Latitude'], bins=20, cmap='Blues', alpha=0.7)
        ax2.scatter(self.fixed_locations['Longitude'], self.fixed_locations['Latitude'], 
                   c='red', s=50, alpha=0.8, edgecolors='black', linewidth=1)
        ax2.set_xlabel('Longitude')
        ax2.set_ylabel('Latitude')
        ax2.set_title('Geographic Density (Red = To Fix)')
        
        # Plot 3: Priority analysis
        if len(self.fixed_locations) > 0:
            priorities = self.fixed_locations['Priority'].values
            ax3.bar(range(1, len(priorities)+1), priorities, color='red', alpha=0.7)
            ax3.set_xlabel('Fix Order')
            ax3.set_ylabel('Priority Number')
            ax3.set_title('Fix Priority Order')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Statistics
        ax4.axis('off')
        stats_text = f"""
        OPTIMIZATION RESULTS SUMMARY
        
        Optimization Method: {self.optimization_method.title()}
        """
        
        if self.optimization_method == 'mixed':
            stats_text += f"Distance Weight: {self.distance_weight:.1f}\n"
            stats_text += f"Time Weight: {self.time_weight:.1f}\n"
        
        stats_text += f"""
        
        Total Locations: {len(self.df)}
        Locations to Fix: {len(self.fixed_locations)}
        Remaining Locations: {len(self.remaining_locations)}
        
        Geographic Bounds:
        Latitude: {self.df['Latitude'].min():.6f} to {self.df['Latitude'].max():.6f}
        Longitude: {self.df['Longitude'].min():.6f} to {self.df['Longitude'].max():.6f}
        
        Fix Priority Range: {self.fixed_locations['Priority'].min():.0f} to {self.fixed_locations['Priority'].max():.0f}
        """
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def save_maps(self, output_dir: str = "visualizations"):
        """Save all visualizations to files."""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Base filename from CSV
        base_name = os.path.splitext(os.path.basename(self.csv_file))[0]
        
        print(f"Creating visualizations for {base_name}...")
        
        # Create and save regular map
        print("  Creating interactive street map...")
        street_map = self.create_folium_map("street")
        street_map_file = os.path.join(output_dir, f"{base_name}_street_map.html")
        street_map.save(street_map_file)
        
        # Create and save satellite map
        print("  Creating interactive satellite map...")
        satellite_map = self.create_folium_map("satellite")
        satellite_map_file = os.path.join(output_dir, f"{base_name}_satellite_map.html")
        satellite_map.save(satellite_map_file)
        
        # Create and save matplotlib overview
        print("  Creating overview plots...")
        fig = self.create_matplotlib_overview()
        overview_file = os.path.join(output_dir, f"{base_name}_overview.png")
        fig.savefig(overview_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"\nVisualizations saved to '{output_dir}' directory:")
        print(f"  • Street Map: {street_map_file}")
        print(f"  • Satellite Map: {satellite_map_file}")
        print(f"  • Overview Plot: {overview_file}")
        
        return street_map_file, satellite_map_file, overview_file
    
    def show_interactive_maps(self, output_dir: str = "visualizations"):
        """Create and open interactive maps in browser."""
        street_map_file, satellite_map_file, overview_file = self.save_maps(output_dir)
        
        # Open maps in browser
        try:
            print(f"\nOpening maps in your default browser...")
            webbrowser.open(f'file://{os.path.abspath(street_map_file)}')
            webbrowser.open(f'file://{os.path.abspath(satellite_map_file)}')
            print("Maps opened successfully!")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please manually open: {os.path.abspath(street_map_file)}")
            print(f"                     {os.path.abspath(satellite_map_file)}")
    
    def create_distance_analysis(self) -> plt.Figure:
        """Create distance analysis plots."""
        if len(self.fixed_locations) < 2:
            print("Need at least 2 fix locations for distance analysis")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Calculate distances between consecutive fix locations
        fix_coords = self.fixed_locations[['Latitude', 'Longitude']].values
        distances = []
        
        for i in range(len(fix_coords) - 1):
            lat1, lon1 = fix_coords[i]
            lat2, lon2 = fix_coords[i + 1]
            # Simple distance calculation (could be improved with actual road distances)
            dist = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Rough km conversion
            distances.append(dist)
        
        # Plot 1: Distance between consecutive fixes
        ax1.plot(range(1, len(distances) + 1), distances, 'o-', color='red', linewidth=2, markersize=6)
        ax1.set_xlabel('Fix Sequence')
        ax1.set_ylabel('Distance to Next Location (km)')
        ax1.set_title('Distance Between Consecutive Fix Locations')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cumulative distance
        cumulative_dist = np.cumsum([0] + distances)
        ax2.plot(range(len(cumulative_dist)), cumulative_dist, 's-', color='blue', linewidth=2, markersize=6)
        ax2.set_xlabel('Fix Location Number')
        ax2.set_ylabel('Cumulative Distance (km)')
        ax2.set_title('Cumulative Distance for Fix Route')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

def main():
    print("TSP Results Visualizer")
    print("=" * 30)
    
    # Look for CSV files in the current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and ('fix_schedule' in f or 'optimized_route' in f)]
    
    if not csv_files:
        print("No TSP result CSV files found in the current directory.")
        print("Please make sure you have run the optimization first.")
        return
    
    print("Available result files:")
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file}")
    
    # Get user choice
    while True:
        try:
            choice = int(input(f"\nSelect a file to visualize (1-{len(csv_files)}): "))
            if 1 <= choice <= len(csv_files):
                selected_file = csv_files[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(csv_files)}")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nLoading results from: {selected_file}")
    
    try:
        # Create visualizer
        visualizer = TSPResultVisualizer(selected_file)
        
        # Ask what type of visualization to create
        print("\nVisualization Options:")
        print("1. Interactive maps (street + satellite)")
        print("2. Overview plots only")
        print("3. All visualizations")
        
        while True:
            try:
                viz_choice = int(input("Choose visualization type (1-3): "))
                if viz_choice in [1, 2, 3]:
                    break
                else:
                    print("Please enter 1, 2, or 3")
            except ValueError:
                print("Please enter a valid number")
        
        if viz_choice in [1, 3]:
            # Create interactive maps
            visualizer.show_interactive_maps()
        
        if viz_choice in [2, 3]:
            # Create overview plots
            print("Creating overview visualization...")
            fig = visualizer.create_matplotlib_overview()
            plt.show()
            
            # Create distance analysis
            print("Creating distance analysis...")
            dist_fig = visualizer.create_distance_analysis()
            if dist_fig:
                plt.show()
        
        if viz_choice == 3:
            print("\nAll visualizations created!")
            print("Check the 'visualizations' folder for saved files.")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")
        print("Please make sure the CSV file is valid and contains the required columns.")

if __name__ == "__main__":
    main()
