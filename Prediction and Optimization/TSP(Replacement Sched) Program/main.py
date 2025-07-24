import pandas as pd
import numpy as np
from tsp_solver import TSPSolver
from typing import List, Tuple, Set
import time

class OptimalFixScheduler:
    def __init__(self, csv_file: str):
        """Initialize the fix scheduler with TSP solver."""
        self.tsp_solver = TSPSolver(csv_file)
        self.n_locations = self.tsp_solver.n_locations
        self.locations = self.tsp_solver.locations
        self.distance_matrix = self.tsp_solver.distance_matrix
        
    def calculate_remaining_route_distance(self, fixed_locations: Set[int]) -> float:
        """Calculate the optimal route distance for remaining (unfixed) locations."""
        remaining_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
        
        if len(remaining_locations) <= 1:
            return 0.0
        
        # Create a temporary TSP solver for remaining locations
        temp_locations = [self.locations[i] for i in remaining_locations]
        
        # Create distance matrix for remaining locations
        n_remaining = len(remaining_locations)
        temp_distance_matrix = np.zeros((n_remaining, n_remaining))
        
        for i in range(n_remaining):
            for j in range(n_remaining):
                if i != j:
                    orig_i = remaining_locations[i]
                    orig_j = remaining_locations[j]
                    temp_distance_matrix[i][j] = self.distance_matrix[orig_i][orig_j]
        
        # Solve TSP for remaining locations
        if n_remaining <= 10:
            # Use brute force for small remaining sets
            from itertools import permutations
            best_distance = float('inf')
            for perm in permutations(range(1, n_remaining)):
                route = [0] + list(perm)
                total_distance = 0
                for k in range(n_remaining):
                    from_idx = route[k]
                    to_idx = route[(k + 1) % n_remaining]
                    total_distance += temp_distance_matrix[from_idx][to_idx]
                best_distance = min(best_distance, total_distance)
            return best_distance
        else:
            # Use nearest neighbor + 2-opt for larger sets
            return self._solve_remaining_nn_2opt(temp_distance_matrix, n_remaining)
    
    def _solve_remaining_nn_2opt(self, distance_matrix: np.ndarray, n: int) -> float:
        """Solve TSP using nearest neighbor + 2-opt for remaining locations."""
        best_distance = float('inf')
        
        # Try multiple starting points
        for start in range(min(5, n)):
            # Nearest neighbor
            unvisited = set(range(n))
            current = start
            route = [current]
            unvisited.remove(current)
            
            while unvisited:
                nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
                route.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Calculate distance
            distance = 0
            for i in range(n):
                from_idx = route[i]
                to_idx = route[(i + 1) % n]
                distance += distance_matrix[from_idx][to_idx]
            
            # Simple 2-opt improvement
            improved = True
            while improved:
                improved = False
                for i in range(n - 1):
                    for j in range(i + 1, n):
                        new_route = route[:]
                        new_route[i:j+1] = reversed(new_route[i:j+1])
                        
                        new_distance = 0
                        for k in range(n):
                            from_idx = new_route[k]
                            to_idx = new_route[(k + 1) % n]
                            new_distance += distance_matrix[from_idx][to_idx]
                        
                        if new_distance < distance:
                            route = new_route
                            distance = new_distance
                            improved = True
            
            best_distance = min(best_distance, distance)
        
        return best_distance
    
    def find_optimal_fixes_greedy(self, num_fixes: int) -> Tuple[List[int], float]:
        """Find the optimal locations to fix using greedy approach."""
        if num_fixes >= self.n_locations:
            return list(range(self.n_locations)), 0.0
        
        fixed_locations = set()
        
        print(f"Finding optimal {num_fixes} locations to fix...")
        print("This may take a moment for larger datasets...")
        
        for fix_round in range(num_fixes):
            best_location = None
            best_remaining_distance = float('inf')
            
            # Try fixing each unfixed location
            unfixed_locations = [i for i in range(self.n_locations) if i not in fixed_locations]
            
            print(f"  Round {fix_round + 1}/{num_fixes}: Testing {len(unfixed_locations)} candidates...")
            
            for candidate in unfixed_locations:
                test_fixed = fixed_locations.copy()
                test_fixed.add(candidate)
                
                remaining_distance = self.calculate_remaining_route_distance(test_fixed)
                
                if remaining_distance < best_remaining_distance:
                    best_remaining_distance = remaining_distance
                    best_location = candidate
            
            if best_location is not None:
                fixed_locations.add(best_location)
                print(f"    Selected location {best_location} (remaining route: {best_remaining_distance:.2f} km)")
            
        final_remaining_distance = self.calculate_remaining_route_distance(fixed_locations)
        return list(fixed_locations), final_remaining_distance
    
    def analyze_fix_impact(self, fixed_locations: List[int]) -> dict:
        """Analyze the impact of fixing specific locations."""
        # Calculate original full route
        if self.n_locations <= 10:
            original_route, original_distance = self.tsp_solver.solve_tsp('brute_force')
        else:
            original_route, original_distance = self.tsp_solver.solve_tsp('nearest_neighbor')
        
        # Calculate remaining route after fixes
        remaining_distance = self.calculate_remaining_route_distance(set(fixed_locations))
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
        print(f"WATER METER FIX OPTIMIZATION RESULTS")
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
        
        if analysis['remaining_locations']:
            print(f"\nFirst 5 Remaining Locations:")
            for i, loc_idx in enumerate(analysis['remaining_locations'][:5]):
                lat, lon = self.locations[loc_idx]
                print(f"  Location {loc_idx}: ({lat:.6f}, {lon:.6f})")
            
            if len(analysis['remaining_locations']) > 5:
                print(f"  ... and {len(analysis['remaining_locations']) - 5} more remaining locations")
    
    def save_results(self, analysis: dict, filename: str = 'fix_schedule_results.csv'):
        """Save the fix schedule results to a CSV file."""
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
                'FixOrder': i + 1
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
                'FixOrder': None
            })
        
        df = pd.DataFrame(results_data)
        df.to_csv(filename, index=False)
        print(f"\nResults saved to '{filename}'")

def main():
    print("Water Meter Fix Schedule Optimizer")
    print("=" * 50)
    
    # Initialize the fix scheduler
    print("Loading water meter location data...")
    try:
        scheduler = OptimalFixScheduler('Watermeterlocation.csv')
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
    fixed_locations, remaining_distance = scheduler.find_optimal_fixes_greedy(num_fixes)
    end_time = time.time()
    
    # Analyze results
    analysis = scheduler.analyze_fix_impact(fixed_locations)
    
    print(f"\nOptimization completed in {end_time - start_time:.2f} seconds")
    
    # Display results
    scheduler.print_results(analysis)
    
    # Save results
    scheduler.save_results(analysis)
    
    # Additional insights
    print(f"\nOptimization Insights:")
    print(f"  Average distance saved per fix: {analysis['distance_saved']/num_fixes:.2f} km")
    print(f"  Remaining average distance per location: {analysis['remaining_distance']/analysis['locations_remaining']:.2f} km")
    
    if analysis['percentage_saved'] > 30:
        print(f"  ✓ Excellent optimization! Over 30% distance reduction achieved.")
    elif analysis['percentage_saved'] > 15:
        print(f"  ✓ Good optimization! Significant distance reduction achieved.")
    else:
        print(f"  ⚠ Limited optimization potential with current fix count.")

if __name__ == "__main__":
    main()
