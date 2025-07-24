import pandas as pd
import numpy as np
from simple_tsp import SimpleTSP
from typing import List, Tuple, Set
import time

class FastFixScheduler:
    def __init__(self, csv_file: str):
        """Initialize the fix scheduler with fast TSP solver."""
        self.tsp_solver = SimpleTSP(csv_file)
        self.n_locations = self.tsp_solver.n_locations
        self.locations = self.tsp_solver.locations
        self.distance_matrix = self.tsp_solver.distance_matrix
        
    def fast_remaining_distance(self, fixed_locations: Set[int]) -> float:
        """Quick approximation of remaining route distance."""
        remaining_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
        
        if len(remaining_locations) <= 1:
            return 0.0
        
        # Use simple nearest neighbor (no 2-opt) for speed
        n_remaining = len(remaining_locations)
        temp_distance_matrix = np.zeros((n_remaining, n_remaining))
        
        for i in range(n_remaining):
            for j in range(n_remaining):
                if i != j:
                    orig_i = remaining_locations[i]
                    orig_j = remaining_locations[j]
                    temp_distance_matrix[i][j] = self.distance_matrix[orig_i][orig_j]
        
        # Quick nearest neighbor only
        unvisited = set(range(n_remaining))
        current = 0
        route = [current]
        unvisited.remove(current)
        total_distance = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: temp_distance_matrix[current][x])
            total_distance += temp_distance_matrix[current][nearest]
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to start
        total_distance += temp_distance_matrix[current][0]
        return total_distance
    
    def find_optimal_fixes_fast(self, num_fixes: int) -> Tuple[List[int], float]:
        """Find optimal locations to fix using fast approximation."""
        if num_fixes >= self.n_locations:
            return list(range(self.n_locations)), 0.0
        
        fixed_locations = set()
        
        print(f"Finding optimal {num_fixes} locations to fix (FAST MODE)...")
        
        for fix_round in range(num_fixes):
            best_location = None
            best_remaining_distance = float('inf')
            
            unfixed_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
            print(f"  Round {fix_round + 1}/{num_fixes}: Testing {len(unfixed_locations)} candidates...")
            
            for candidate in unfixed_locations:
                test_fixed = fixed_locations.copy()
                test_fixed.add(candidate)
                
                # Use fast approximation
                remaining_distance = self.fast_remaining_distance(test_fixed)
                
                if remaining_distance < best_remaining_distance:
                    best_remaining_distance = remaining_distance
                    best_location = candidate
            
            if best_location is not None:
                fixed_locations.add(best_location)
                print(f"    Selected location {best_location} (remaining route: {best_remaining_distance:.2f} km)")
        
        final_remaining_distance = self.fast_remaining_distance(fixed_locations)
        return list(fixed_locations), final_remaining_distance
    
    def analyze_fix_impact(self, fixed_locations: List[int]) -> dict:
        """Analyze the impact of fixing specific locations."""
        # Use simple TSP solver for speed
        original_route, original_distance = self.tsp_solver.solve_tsp()
        
        # Calculate remaining route after fixes
        remaining_distance = self.fast_remaining_distance(set(fixed_locations))
        remaining_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
        
        # Calculate savings
        distance_saved = original_distance - remaining_distance
        percentage_saved = (distance_saved / original_distance) * 100 if original_distance > 0 else 0
        
        return {
            'original_distance': original_distance,
            'remaining_distance': remaining_distance,
            'distance_saved': distance_saved,
            'percentage_saved': percentage_saved,
            'locations_fixed': len(fixed_locations),
            'locations_remaining': len(remaining_locations),
            'fixed_locations': fixed_locations,
            'remaining_locations': remaining_locations
        }
    
    def print_results(self, analysis: dict):
        """Print detailed results of the fix analysis."""
        print(f"\n{'='*60}")
        print(f"WATER METER FIX OPTIMIZATION RESULTS (FAST MODE)")
        print(f"{'='*60}")
        
        print(f"Original Route Distance: {analysis['original_distance']:.2f} km")
        print(f"Remaining Route Distance: {analysis['remaining_distance']:.2f} km")
        print(f"Distance Saved: {analysis['distance_saved']:.2f} km")
        print(f"Percentage Saved: {analysis['percentage_saved']:.1f}%")
        
        print(f"\nLocation Summary:")
        print(f"  Total Locations: {analysis['locations_fixed'] + analysis['locations_remaining']}")
        print(f"  Locations to Fix: {analysis['locations_fixed']}")
        print(f"  Remaining Locations: {analysis['locations_remaining']}")
        
        print(f"\nLocations to Fix (Priority Order):")
        for i, loc_idx in enumerate(analysis['fixed_locations']):
            lat, lon = self.locations[loc_idx]
            print(f"  {i+1}. Location {loc_idx}: ({lat:.6f}, {lon:.6f})")

def main():
    print("Water Meter Fix Schedule Optimizer - FAST MODE")
    print("=" * 55)
    
    # Initialize the fix scheduler
    print("Loading water meter location data...")
    try:
        scheduler = FastFixScheduler('Watermeterlocation.csv')
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
    
    print(f"\nOptimizing fix schedule for {num_fixes} water meters...")
    
    # Find optimal fixes
    start_time = time.time()
    fixed_locations, remaining_distance = scheduler.find_optimal_fixes_fast(num_fixes)
    end_time = time.time()
    
    # Analyze results
    analysis = scheduler.analyze_fix_impact(fixed_locations)
    
    print(f"\nOptimization completed in {end_time - start_time:.2f} seconds")
    
    # Display results
    scheduler.print_results(analysis)
    
    # Additional insights
    print(f"\nOptimization Insights:")
    print(f"  Average distance saved per fix: {analysis['distance_saved']/num_fixes:.2f} km")
    if analysis['locations_remaining'] > 0:
        print(f"  Remaining average distance per location: {analysis['remaining_distance']/analysis['locations_remaining']:.2f} km")
    
    if analysis['percentage_saved'] > 30:
        print(f"  ✓ Excellent optimization! Over 30% distance reduction achieved.")
    elif analysis['percentage_saved'] > 15:
        print(f"  ✓ Good optimization! Significant distance reduction achieved.")
    else:
        print(f"  ⚠ Limited optimization potential with current fix count.")
    
    print(f"\nNote: This is FAST MODE with approximations for speed.")
    print(f"For more accurate results, use the full optimization mode.")

if __name__ == "__main__":
    main()
