import csv
import math
import time
from typing import List, Tuple

class OptimizedTSP:
    def __init__(self, csv_file: str):
        """Initialize TSP solver with water meter location data."""
        self.locations = []
        self.load_data(csv_file)
        self.n_locations = len(self.locations)
        
    def load_data(self, csv_file: str):
        """Load location data from CSV file."""
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                self.locations.append((lat, lon))
    
    def haversine_distance(self, idx1: int, idx2: int) -> float:
        """Calculate the great circle distance between two locations in kilometers."""
        lat1, lon1 = self.locations[idx1]
        lat2, lon2 = self.locations[idx2]
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def calculate_route_distance(self, route: List[int]) -> float:
        """Calculate total distance for a given route."""
        total_distance = 0
        for i in range(len(route)):
            from_idx = route[i]
            to_idx = route[(i + 1) % len(route)]  # Return to start
            total_distance += self.haversine_distance(from_idx, to_idx)
        return total_distance
    
    def nearest_neighbor_tsp(self, start_city: int = 0) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor heuristic."""
        unvisited = set(range(self.n_locations))
        current_city = start_city
        route = [current_city]
        unvisited.remove(current_city)
        
        while unvisited:
            nearest_city = min(unvisited, key=lambda city: self.haversine_distance(current_city, city))
            route.append(nearest_city)
            unvisited.remove(nearest_city)
            current_city = nearest_city
        
        return route, self.calculate_route_distance(route)
    
    def solve_tsp_quick(self) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor from multiple starting points."""
        best_route = None
        best_distance = float('inf')
        
        # Try 5 different starting points
        start_points = [0, self.n_locations//4, self.n_locations//2, 3*self.n_locations//4, self.n_locations-1]
        
        for start in start_points:
            route, distance = self.nearest_neighbor_tsp(start)
            if distance < best_distance:
                best_distance = distance
                best_route = route
        
        return best_route, best_distance
    
    def save_route_to_csv(self, route: List[int], filename: str = 'optimized_route.csv'):
        """Save the optimized route to a CSV file."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Order', 'LocationIndex', 'Latitude', 'Longitude', 'Distance_to_Next'])
            
            for i, location_idx in enumerate(route):
                lat, lon = self.locations[location_idx]
                next_idx = route[(i + 1) % len(route)]
                distance_to_next = self.haversine_distance(location_idx, next_idx)
                writer.writerow([i+1, location_idx, lat, lon, f"{distance_to_next:.3f}"])
    
    def print_summary(self, route: List[int], distance: float):
        """Print a summary of the route."""
        print(f"\n{'='*60}")
        print(f"WATER METER TSP SOLUTION")
        print(f"{'='*60}")
        print(f"Total Distance: {distance:.2f} km")
        print(f"Number of Locations: {len(route)}")
        print(f"Average distance per stop: {distance/len(route):.2f} km")
        
        print(f"\nFirst 10 locations in route:")
        for i in range(min(10, len(route))):
            location_idx = route[i]
            lat, lon = self.locations[location_idx]
            print(f"  {i+1}. Location {location_idx}: ({lat:.6f}, {lon:.6f})")
        
        if len(route) > 10:
            print(f"  ... and {len(route) - 10} more locations")

def main():
    print("Water Meter TSP Solver - Optimized Version")
    print("=" * 45)
    
    # Initialize TSP solver
    print("Loading water meter location data...")
    try:
        tsp = OptimizedTSP('Watermeterlocation.csv')
    except FileNotFoundError:
        print("Error: Watermeterlocation.csv not found!")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print(f"Loaded {tsp.n_locations} water meter locations")
    
    # Calculate bounds
    lats = [loc[0] for loc in tsp.locations]
    lons = [loc[1] for loc in tsp.locations]
    
    print(f"Geographic coverage:")
    print(f"  Latitude: {min(lats):.6f} to {max(lats):.6f}")
    print(f"  Longitude: {min(lons):.6f} to {max(lons):.6f}")
    
    # Solve TSP
    print(f"\nSolving TSP using Nearest Neighbor heuristic...")
    start_time = time.time()
    best_route, best_distance = tsp.solve_tsp_quick()
    end_time = time.time()
    
    # Display results
    print(f"Solution found in {end_time - start_time:.2f} seconds")
    tsp.print_summary(best_route, best_distance)
    
    # Save results
    tsp.save_route_to_csv(best_route)
    print(f"\nOptimized route saved to 'optimized_route.csv'")
    
    # Additional statistics
    print(f"\nRoute Statistics:")
    print(f"  Starting location: {best_route[0]}")
    print(f"  Route: {' -> '.join(map(str, best_route[:5]))} -> ... -> {best_route[0]} (return)")
    print(f"  Estimated travel time (at 30 mph): {best_distance * 0.621371 / 30:.1f} hours")

if __name__ == "__main__":
    main()
