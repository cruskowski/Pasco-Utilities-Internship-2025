import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import permutations
import math
from typing import List, Tuple
import time

class TSPSolver:
    def __init__(self, csv_file: str):
        """Initialize TSP solver with water meter location data."""
        self.data = pd.read_csv(csv_file)
        self.locations = self.data[['Latitude', 'Longitude']].values
        self.n_locations = len(self.locations)
        self.distance_matrix = self._calculate_distance_matrix()
        
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _calculate_distance_matrix(self) -> np.ndarray:
        """Calculate distance matrix between all pairs of locations."""
        n = self.n_locations
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = self.locations[i]
                    lat2, lon2 = self.locations[j]
                    distance_matrix[i][j] = self._haversine_distance(lat1, lon1, lat2, lon2)
        
        return distance_matrix
    
    def calculate_route_distance(self, route: List[int]) -> float:
        """Calculate total distance for a given route."""
        total_distance = 0
        for i in range(len(route)):
            from_idx = route[i]
            to_idx = route[(i + 1) % len(route)]  # Return to start
            total_distance += self.distance_matrix[from_idx][to_idx]
        return total_distance
    
    def brute_force_tsp(self) -> Tuple[List[int], float]:
        """Solve TSP using brute force (only for small datasets)."""
        if self.n_locations > 10:
            raise ValueError("Brute force is too slow for more than 10 locations")
        
        best_route = None
        best_distance = float('inf')
        
        # Fix the first city and permute the rest
        for perm in permutations(range(1, self.n_locations)):
            route = [0] + list(perm)
            distance = self.calculate_route_distance(route)
            if distance < best_distance:
                best_distance = distance
                best_route = route
        
        return best_route, best_distance
    
    def nearest_neighbor_tsp(self, start_city: int = 0) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor heuristic."""
        unvisited = set(range(self.n_locations))
        current_city = start_city
        route = [current_city]
        unvisited.remove(current_city)
        
        while unvisited:
            nearest_city = min(unvisited, key=lambda city: self.distance_matrix[current_city][city])
            route.append(nearest_city)
            unvisited.remove(nearest_city)
            current_city = nearest_city
        
        return route, self.calculate_route_distance(route)
    
    def two_opt_improvement(self, route: List[int]) -> Tuple[List[int], float]:
        """Improve a route using 2-opt local search."""
        best_route = route[:]
        best_distance = self.calculate_route_distance(best_route)
        improved = True
        
        while improved:
            improved = False
            for i in range(len(route) - 1):
                for j in range(i + 1, len(route)):
                    # Create new route by reversing the segment between i and j
                    new_route = route[:]
                    new_route[i:j+1] = reversed(new_route[i:j+1])
                    
                    new_distance = self.calculate_route_distance(new_route)
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
            
            route = best_route
        
        return best_route, best_distance
    
    def solve_tsp(self, method: str = 'nearest_neighbor') -> Tuple[List[int], float]:
        """Solve TSP using specified method."""
        if method == 'brute_force':
            return self.brute_force_tsp()
        elif method == 'nearest_neighbor':
            route, distance = self.nearest_neighbor_tsp()
            return self.two_opt_improvement(route)
        else:
            raise ValueError("Method must be 'brute_force' or 'nearest_neighbor'")
    
    def plot_route(self, route: List[int], title: str = "TSP Route"):
        """Plot the route on a map."""
        plt.figure(figsize=(12, 8))
        
        # Plot all locations
        lats = [self.locations[i][0] for i in range(self.n_locations)]
        lons = [self.locations[i][1] for i in range(self.n_locations)]
        plt.scatter(lons, lats, c='red', s=50, alpha=0.7, label='Water Meters')
        
        # Plot route
        route_lats = [self.locations[i][0] for i in route] + [self.locations[route[0]][0]]
        route_lons = [self.locations[i][1] for i in route] + [self.locations[route[0]][1]]
        plt.plot(route_lons, route_lats, 'b-', linewidth=2, alpha=0.7, label='Route')
        
        # Mark start point
        start_lat, start_lon = self.locations[route[0]]
        plt.scatter(start_lon, start_lat, c='green', s=100, marker='s', label='Start/End')
        
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def get_route_summary(self, route: List[int], distance: float) -> str:
        """Get a summary of the route."""
        summary = f"Route Summary:\n"
        summary += f"Total Distance: {distance:.2f} km\n"
        summary += f"Number of Locations: {len(route)}\n"
        summary += f"Route Order: {' -> '.join(map(str, route))} -> {route[0]}\n\n"
        
        summary += "Detailed Route:\n"
        for i, location_idx in enumerate(route):
            lat, lon = self.locations[location_idx]
            summary += f"{i+1}. Location {location_idx}: ({lat:.6f}, {lon:.6f})\n"
        
        return summary

def main():
    # Initialize TSP solver
    print("Loading water meter location data...")
    tsp = TSPSolver('Watermeterlocation.csv')
    
    print(f"Loaded {tsp.n_locations} water meter locations")
    print(f"Geographic bounds:")
    print(f"  Latitude: {tsp.data['Latitude'].min():.6f} to {tsp.data['Latitude'].max():.6f}")
    print(f"  Longitude: {tsp.data['Longitude'].min():.6f} to {tsp.data['Longitude'].max():.6f}")
    
    # For large datasets, use nearest neighbor with 2-opt improvement
    if tsp.n_locations > 10:
        print(f"\nUsing Nearest Neighbor + 2-opt for {tsp.n_locations} locations...")
        method = 'nearest_neighbor'
    else:
        print(f"\nUsing Brute Force for {tsp.n_locations} locations...")
        method = 'brute_force'
    
    # Solve TSP
    start_time = time.time()
    best_route, best_distance = tsp.solve_tsp(method)
    end_time = time.time()
    
    # Display results
    print(f"\nSolution found in {end_time - start_time:.2f} seconds")
    print(f"Best route distance: {best_distance:.2f} km")
    print(f"Route: {' -> '.join(map(str, best_route))} -> {best_route[0]}")
    
    # Plot the route
    tsp.plot_route(best_route, f"Water Meter TSP Route ({method})")
    
    # Save detailed results
    with open('tsp_results.txt', 'w') as f:
        f.write(tsp.get_route_summary(best_route, best_distance))
        f.write(f"\nSolution Method: {method}\n")
        f.write(f"Computation Time: {end_time - start_time:.2f} seconds\n")
    
    print("\nDetailed results saved to 'tsp_results.txt'")

if __name__ == "__main__":
    main()
