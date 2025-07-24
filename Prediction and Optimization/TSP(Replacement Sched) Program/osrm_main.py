import pandas as pd
import numpy as np
from osrm_tsp import OSRMTSPSolver
from typing import List, Tuple, Set
import time

class OSRMFixScheduler:
    def __init__(self, csv_file: str, osrm_server: str = "http://router.project-osrm.org"):
        """Initialize the OSRM-based fix scheduler."""
        self.osrm_solver = OSRMTSPSolver(csv_file, osrm_server)
        self.n_locations = self.osrm_solver.n_locations
        self.locations = self.osrm_solver.locations
        
        # Get OSRM matrices
        print("Initializing OSRM routing data...")
        self.distance_matrix, self.duration_matrix = self.osrm_solver.get_osrm_matrix()
        
    def calculate_remaining_route_value(self, fixed_locations: Set[int], use_duration: bool = False, 
                                       distance_weight: float = 1.0, time_weight: float = 0.0) -> float:
        """Calculate the optimal route value for remaining (unfixed) locations."""
        remaining_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
        
        if len(remaining_locations) <= 1:
            return 0.0
        
        # Handle mixed optimization
        if distance_weight > 0 and time_weight > 0:
            # Create combined matrix for mixed optimization
            matrix = self._create_combined_matrix(distance_weight, time_weight)
        else:
            matrix = self.duration_matrix if use_duration else self.distance_matrix
        
        # Create matrix for remaining locations
        n_remaining = len(remaining_locations)
        temp_matrix = np.zeros((n_remaining, n_remaining))
        
        for i in range(n_remaining):
            for j in range(n_remaining):
                if i != j:
                    orig_i = remaining_locations[i]
                    orig_j = remaining_locations[j]
                    temp_matrix[i][j] = matrix[orig_i][orig_j]
        
        # Quick nearest neighbor solution for remaining locations
        best_value = float('inf')
        
        # Try a few starting points
        for start in range(min(3, n_remaining)):
            unvisited = set(range(n_remaining))
            current = start
            route = [current]
            unvisited.remove(current)
            total_value = 0
            
            while unvisited:
                nearest = min(unvisited, key=lambda x: temp_matrix[current][x])
                total_value += temp_matrix[current][nearest]
                route.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Return to start
            total_value += temp_matrix[current][0]
            best_value = min(best_value, total_value)
        
        return best_value
    
    def _create_combined_matrix(self, distance_weight: float, time_weight: float) -> np.ndarray:
        """Create a combined matrix using weighted distance and time."""
        # Normalize matrices to similar scales
        distance_normalized = self.distance_matrix / np.max(self.distance_matrix)
        time_normalized = self.duration_matrix / np.max(self.duration_matrix)
        
        # Create weighted combination
        combined_matrix = (distance_weight * distance_normalized + 
                          time_weight * time_normalized)
        
        return combined_matrix
    
    def find_optimal_fixes_osrm(self, num_fixes: int, optimization_method: str = "distance", 
                               distance_weight: float = 1.0, time_weight: float = 0.0) -> Tuple[List[int], float]:
        """Find optimal locations to fix using OSRM routing data."""
        if num_fixes >= self.n_locations:
            return list(range(self.n_locations)), 0.0
        
        fixed_locations = set()
        
        if optimization_method == "mixed":
            print(f"Finding optimal {num_fixes} locations to fix (OSRM - Mixed: {distance_weight:.1f}x distance + {time_weight:.1f}x time)...")
        else:
            optimization_type = "travel time" if optimization_method == "time" else "distance"
            print(f"Finding optimal {num_fixes} locations to fix (OSRM - {optimization_type})...")
        
        for fix_round in range(num_fixes):
            best_location = None
            best_remaining_value = float('inf')
            
            unfixed_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
            print(f"  Round {fix_round + 1}/{num_fixes}: Testing {len(unfixed_locations)} candidates...")
            
            for candidate in unfixed_locations:
                test_fixed = fixed_locations.copy()
                test_fixed.add(candidate)
                
                if optimization_method == "mixed":
                    remaining_value = self.calculate_remaining_route_value(
                        test_fixed, use_duration=False, 
                        distance_weight=distance_weight, time_weight=time_weight
                    )
                else:
                    use_duration = optimization_method == "time"
                    remaining_value = self.calculate_remaining_route_value(test_fixed, use_duration)
                
                if remaining_value < best_remaining_value:
                    best_remaining_value = remaining_value
                    best_location = candidate
            
            if best_location is not None:
                fixed_locations.add(best_location)
                if optimization_method == "mixed":
                    print(f"    Selected location {best_location} (remaining weighted score: {best_remaining_value:.3f})")
                else:
                    unit = "min" if optimization_method == "time" else "km"
                    print(f"    Selected location {best_location} (remaining route: {best_remaining_value:.2f} {unit})")
        
        if optimization_method == "mixed":
            final_remaining_value = self.calculate_remaining_route_value(
                fixed_locations, use_duration=False, 
                distance_weight=distance_weight, time_weight=time_weight
            )
        else:
            use_duration = optimization_method == "time"
            final_remaining_value = self.calculate_remaining_route_value(fixed_locations, use_duration)
        
        return list(fixed_locations), final_remaining_value
    
    def analyze_fix_impact_osrm(self, fixed_locations: List[int], optimization_method: str = "distance",
                               distance_weight: float = 1.0, time_weight: float = 0.0) -> dict:
        """Analyze the impact of fixing specific locations using OSRM data."""
        # Calculate original full route
        if optimization_method == "mixed":
            # For mixed optimization, we'll use distance as base but include both metrics
            original_route, original_value = self.osrm_solver.solve_tsp(use_duration=False, max_starts=5)
        else:
            use_duration = optimization_method == "time"
            original_route, original_value = self.osrm_solver.solve_tsp(use_duration=use_duration, max_starts=5)
        
        # Calculate remaining route after fixes
        if optimization_method == "mixed":
            remaining_value = self.calculate_remaining_route_value(
                set(fixed_locations), use_duration=False,
                distance_weight=distance_weight, time_weight=time_weight
            )
        else:
            use_duration = optimization_method == "time"
            remaining_value = self.calculate_remaining_route_value(set(fixed_locations), use_duration)
        
        remaining_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
        
        # Calculate savings
        value_saved = original_value - remaining_value
        percentage_saved = (value_saved / original_value) * 100 if original_value > 0 else 0
        
        # Get both distance and time metrics
        original_distance = self.osrm_solver.calculate_route_distance(original_route, use_duration=False)
        original_time = self.osrm_solver.calculate_route_distance(original_route, use_duration=True)
        remaining_distance = self.calculate_remaining_route_value(set(fixed_locations), use_duration=False)
        remaining_time = self.calculate_remaining_route_value(set(fixed_locations), use_duration=True)
        
        return {
            'original_value': original_value,
            'remaining_value': remaining_value,
            'value_saved': value_saved,
            'percentage_saved': percentage_saved,
            'original_distance': original_distance,
            'original_time': original_time,
            'remaining_distance': remaining_distance,
            'remaining_time': remaining_time,
            'locations_fixed': len(fixed_locations),
            'locations_remaining': len(remaining_locations),
            'fixed_locations': fixed_locations,
            'remaining_locations': remaining_locations,
            'optimization_method': optimization_method,
            'distance_weight': distance_weight,
            'time_weight': time_weight
        }
    
    def print_results_osrm(self, analysis: dict):
        """Print detailed results of the OSRM fix analysis."""
        print(f"\n{'='*70}")
        print(f"OSRM WATER METER FIX OPTIMIZATION RESULTS")
        print(f"{'='*70}")
        
        opt_method = analysis['optimization_method']
        
        if opt_method == "mixed":
            dist_weight = analysis['distance_weight']
            time_weight = analysis['time_weight']
            print(f"Optimized for: Mixed ({dist_weight:.1f}x Distance + {time_weight:.1f}x Time)")
        else:
            print(f"Optimized for: {opt_method.title()}")
            
        print(f"Original Route Distance: {analysis['original_distance']:.2f} km")
        print(f"Original Route Time: {analysis['original_time']:.1f} min ({analysis['original_time']/60:.1f} hours)")
        print(f"Remaining Route Distance: {analysis['remaining_distance']:.2f} km")
        print(f"Remaining Route Time: {analysis['remaining_time']:.1f} min ({analysis['remaining_time']/60:.1f} hours)")
        
        if opt_method == 'distance':
            print(f"Distance Saved: {analysis['value_saved']:.2f} km ({analysis['percentage_saved']:.1f}%)")
            print(f"Time Saved: {analysis['original_time'] - analysis['remaining_time']:.1f} min")
        elif opt_method == 'time':
            print(f"Time Saved: {analysis['value_saved']:.1f} min ({analysis['percentage_saved']:.1f}%)")
            print(f"Distance Saved: {analysis['original_distance'] - analysis['remaining_distance']:.2f} km")
        else:  # mixed
            print(f"Distance Saved: {analysis['original_distance'] - analysis['remaining_distance']:.2f} km")
            print(f"Time Saved: {analysis['original_time'] - analysis['remaining_time']:.1f} min")
            print(f"Combined Optimization Score Improvement: {analysis['percentage_saved']:.1f}%")
        
        print(f"\nLocation Summary:")
        print(f"  Total Locations: {analysis['locations_fixed'] + analysis['locations_remaining']}")
        print(f"  Locations to Fix: {analysis['locations_fixed']}")
        print(f"  Remaining Locations: {analysis['locations_remaining']}")
        
        print(f"\nLocations to Fix (Priority Order):")
        for i, loc_idx in enumerate(analysis['fixed_locations']):
            lat, lon = self.locations[loc_idx]
            print(f"  {i+1}. Location {loc_idx}: ({lat:.6f}, {lon:.6f})")
        
        if analysis['remaining_locations']:
            print(f"\nFirst 5 Remaining Locations:")
            for i, loc_idx in enumerate(analysis['remaining_locations'][:5]):
                lat, lon = self.locations[loc_idx]
                print(f"  Location {loc_idx}: ({lat:.6f}, {lon:.6f})")
            
            if len(analysis['remaining_locations']) > 5:
                print(f"  ... and {len(analysis['remaining_locations']) - 5} more remaining locations")
    
    def save_results_osrm(self, analysis: dict, filename: str = None):
        """Save the OSRM fix schedule results to a CSV file."""
        if filename is None:
            opt_method = analysis['optimization_method']
            if opt_method == "mixed":
                filename = f'osrm_fix_schedule_mixed_{analysis["distance_weight"]:.1f}d_{analysis["time_weight"]:.1f}t.csv'
            else:
                filename = f'osrm_fix_schedule_{opt_method}_optimized.csv'
        
        # Create results dataframe
        results_data = []
        
        # Add fixed locations
        for i, loc_idx in enumerate(analysis['fixed_locations']):
            lat, lon = self.locations[loc_idx]
            results_data.append({
                'Priority': i + 1,
                'LocationIndex': loc_idx,
                'Latitude': lat,
                'Longitude': lon,
                'Status': 'TO_FIX',
                'FixOrder': i + 1,
                'OptimizationMethod': analysis['optimization_method'],
                'DistanceWeight': analysis.get('distance_weight', 1.0),
                'TimeWeight': analysis.get('time_weight', 0.0)
            })
        
        # Add remaining locations
        for loc_idx in analysis['remaining_locations']:
            lat, lon = self.locations[loc_idx]
            results_data.append({
                'Priority': None,
                'LocationIndex': loc_idx,
                'Latitude': lat,
                'Longitude': lon,
                'Status': 'REMAINING',
                'FixOrder': None,
                'OptimizationMethod': analysis['optimization_method'],
                'DistanceWeight': analysis.get('distance_weight', 1.0),
                'TimeWeight': analysis.get('time_weight', 0.0)
            })
        
        df = pd.DataFrame(results_data)
        df.to_csv(filename, index=False)
        print(f"\nResults saved to '{filename}'")

def main():
    print("OSRM Water Meter Fix Schedule Optimizer")
    print("=" * 55)
    
    # Initialize the OSRM fix scheduler
    print("Loading water meter location data...")
    try:
        # You can specify a local OSRM server here if you have one
        # scheduler = OSRMFixScheduler('Watermeterlocation.csv', 'http://localhost:5000')
        scheduler = OSRMFixScheduler('Watermeterlocation.csv')
    except FileNotFoundError:
        print("Error: Watermeterlocation.csv not found!")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print(f"Loaded {scheduler.n_locations} water meter locations")
    
    # Get user input for number of fixes
    while True:
        try:
            num_fixes = int(input(f"\nHow many water meters do you plan to fix? (1-{scheduler.n_locations-1}): "))
            if 1 <= num_fixes < scheduler.n_locations:
                break
            else:
                print(f"Please enter a number between 1 and {scheduler.n_locations-1}")
        except ValueError:
            print("Please enter a valid number")
    
    # Ask for optimization preference
    print("\nOptimization Options:")
    print("1. Minimize remaining distance (km)")
    print("2. Minimize remaining travel time (minutes)")
    print("3. Mixed optimization (balance both distance and time)")
    
    optimization_method = None
    distance_weight = 1.0
    time_weight = 0.0
    
    while True:
        try:
            choice = int(input("Choose optimization method (1, 2, or 3): "))
            if choice == 1:
                optimization_method = "distance"
                break
            elif choice == 2:
                optimization_method = "time"
                break
            elif choice == 3:
                optimization_method = "mixed"
                # Get weights for mixed optimization
                print("\nFor mixed optimization, specify the relative importance:")
                print("Example: 2.0 distance + 1.0 time = prioritize distance 2x more than time")
                
                while True:
                    try:
                        distance_weight = float(input("Distance weight (e.g., 1.0, 2.0): "))
                        if distance_weight >= 0:
                            break
                        print("Please enter a non-negative number")
                    except ValueError:
                        print("Please enter a valid number")
                
                while True:
                    try:
                        time_weight = float(input("Time weight (e.g., 1.0, 0.5): "))
                        if time_weight >= 0:
                            break
                        print("Please enter a non-negative number")
                    except ValueError:
                        print("Please enter a valid number")
                
                # Normalize weights so they sum to a reasonable value
                total_weight = distance_weight + time_weight
                if total_weight == 0:
                    print("At least one weight must be greater than 0. Setting equal weights.")
                    distance_weight = time_weight = 1.0
                
                break
            else:
                print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nOptimizing fix schedule for {num_fixes} water meters using OSRM...")
    
    # Find optimal fixes
    start_time = time.time()
    fixed_locations, remaining_value = scheduler.find_optimal_fixes_osrm(
        num_fixes, optimization_method, distance_weight, time_weight
    )
    end_time = time.time()
    
    # Analyze results
    analysis = scheduler.analyze_fix_impact_osrm(
        fixed_locations, optimization_method, distance_weight, time_weight
    )
    
    print(f"\nOptimization completed in {end_time - start_time:.2f} seconds")
    
    # Display results
    scheduler.print_results_osrm(analysis)
    
    # Save results
    scheduler.save_results_osrm(analysis)
    
    # Additional insights
    print(f"\nOSRM Optimization Insights:")
    
    if optimization_method == "mixed":
        print(f"  Distance saved: {analysis['original_distance'] - analysis['remaining_distance']:.2f} km")
        print(f"  Time saved: {analysis['original_time'] - analysis['remaining_time']:.1f} min")
        print(f"  Combined optimization score improvement: {analysis['percentage_saved']:.1f}%")
    else:
        opt_type = optimization_method
        unit = "min" if optimization_method == "time" else "km"
        print(f"  Average {opt_type} saved per fix: {analysis['value_saved']/num_fixes:.2f} {unit}")
        
        if analysis['locations_remaining'] > 0:
            remaining_avg = analysis['remaining_value'] / analysis['locations_remaining']
            print(f"  Remaining average {opt_type} per location: {remaining_avg:.2f} {unit}")
    
    if analysis['percentage_saved'] > 30:
        print(f"  ✓ Excellent optimization! Over 30% reduction achieved.")
    elif analysis['percentage_saved'] > 15:
        print(f"  ✓ Good optimization! Significant reduction achieved.")
    else:
        print(f"  ⚠ Limited optimization potential with current fix count.")
    
    print(f"\nNote: Results use real-world road network distances and travel times from OSRM.")

if __name__ == "__main__":
    main()
