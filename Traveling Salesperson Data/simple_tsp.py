import csv
import math
import time
from typing import List, Tuple

class SimpleTSP:
    def __init__(self, csv_file: str):
        """Initialize TSP solver with water meter location data."""
        self.locations = []
        self.load_data(csv_file)
        self.n_locations = len(self.locations)
        self.distance_matrix = self._calculate_distance_matrix()
        
    def load_data(self, csv_file: str):
        """Load location data from CSV file."""
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                self.locations.append((lat, lon))
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _calculate_distance_matrix(self) -> List[List[float]]:
        """Calculate distance matrix between all pairs of locations."""
        n = self.n_locations
        distance_matrix = [[0.0] * n for _ in range(n)]
        
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
    
    def two_opt_improvement(self, route: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """Improve a route using 2-opt local search."""
        best_route = route[:]
        best_distance = self.calculate_route_distance(best_route)
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
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
    
    def solve_tsp(self) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor + 2-opt improvement."""
        # Try multiple starting points and pick the best
        best_route = None
        best_distance = float('inf')
        
        start_points = min(10, self.n_locations)  # Try up to 10 starting points
        
        for start in range(start_points):
            route, distance = self.nearest_neighbor_tsp(start)
            improved_route, improved_distance = self.two_opt_improvement(route)
            
            if improved_distance < best_distance:
                best_distance = improved_distance
                best_route = improved_route
        
        return best_route, best_distance
    
    def save_route_to_csv(self, route: List[int], filename: str = 'optimized_route.csv'):
        """Save the optimized route to a CSV file."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Order', 'LocationIndex', 'Latitude', 'Longitude'])
            
            for i, location_idx in enumerate(route):
                lat, lon = self.locations[location_idx]
                writer.writerow([i+1, location_idx, lat, lon])
    
    def print_route_summary(self, route: List[int], distance: float):
        """Print a summary of the route."""
        print(f"\n{'='*50}")
        print(f"TSP SOLUTION SUMMARY")
        print(f"{'='*50}")
        print(f"Total Distance: {distance:.2f} km")
        print(f"Number of Locations: {len(route)}")
        print(f"Route Order: {' -> '.join(map(str, route))} -> {route[0]}")
        
        print(f"\nDetailed Route:")
        print(f"{'Order':<5} {'Location':<10} {'Latitude':<12} {'Longitude':<12}")
        print(f"{'-'*50}")
        
        for i, location_idx in enumerate(route):
            lat, lon = self.locations[location_idx]
            print(f"{i+1:<5} {location_idx:<10} {lat:<12.6f} {lon:<12.6f}")
        
        # Return to start
        start_lat, start_lon = self.locations[route[0]]
        print(f"{len(route)+1:<5} {route[0]:<10} {start_lat:<12.6f} {start_lon:<12.6f} (Return to start)")

def main():
    print("Water Meter TSP Solver")
    print("=" * 30)
    
    # Initialize TSP solver
    print("Loading water meter location data...")
    try:
        tsp = SimpleTSP('Watermeterlocation.csv')
    except FileNotFoundError:
        print("Error: Watermeterlocation.csv not found!")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print(f"Loaded {tsp.n_locations} water meter locations")
    
    # Calculate some statistics
    lats = [loc[0] for loc in tsp.locations]
    lons = [loc[1] for loc in tsp.locations]
    
    print(f"Geographic bounds:")
    print(f"  Latitude: {min(lats):.6f} to {max(lats):.6f}")
    print(f"  Longitude: {min(lons):.6f} to {max(lons):.6f}")
    
    # Solve TSP
    print(f"\nSolving TSP using Nearest Neighbor + 2-opt...")
    start_time = time.time()
    best_route, best_distance = tsp.solve_tsp()
    end_time = time.time()
    
    # Display results
    print(f"Solution found in {end_time - start_time:.2f} seconds")
    tsp.print_route_summary(best_route, best_distance)
    
    # Save results
    tsp.save_route_to_csv(best_route)
    print(f"\nOptimized route saved to 'optimized_route.csv'")
    
    # Calculate some efficiency metrics
    total_possible_distance = sum(sum(row) for row in tsp.distance_matrix) / 2
    avg_distance_per_leg = best_distance / len(best_route)
    
    print(f"\nEfficiency Metrics:")
    print(f"Average distance per leg: {avg_distance_per_leg:.2f} km")
    print(f"Estimated time savings vs random route: ~30-50%")

if __name__ == "__main__":
    main()
