import pandas as pd
import numpy as np
import requests
import time
from typing import List, Tuple, Dict, Optional
import json
from urllib.parse import urlencode

class OSRMTSPSolver:
    def __init__(self, csv_file: str, osrm_server: str = "http://router.project-osrm.org"):
        """Initialize OSRM TSP solver with water meter location data."""
        self.osrm_server = osrm_server.rstrip('/')
        self.locations = []
        self.load_data(csv_file)
        self.n_locations = len(self.locations)
        self.distance_matrix = None
        self.duration_matrix = None
        
    def load_data(self, csv_file: str):
        """Load location data from CSV file."""
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            self.locations.append((lat, lon))
    
    def get_osrm_matrix(self, batch_size: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Get distance and duration matrices from OSRM."""
        print(f"Fetching real-world distances for {self.n_locations} locations using OSRM...")
        
        if self.n_locations <= batch_size:
            return self._get_single_matrix()
        else:
            return self._get_batched_matrix(batch_size)
    
    def _get_single_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get matrix for all locations in one request."""
        # Prepare coordinates string for OSRM
        coords = ";".join([f"{lon},{lat}" for lat, lon in self.locations])
        
        # OSRM matrix API endpoint
        url = f"{self.osrm_server}/table/v1/driving/{coords}"
        
        params = {
            'annotations': 'distance,duration'
        }
        
        try:
            print("  Making OSRM API request...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] != 'Ok':
                raise Exception(f"OSRM API error: {data.get('message', 'Unknown error')}")
            
            # Convert to numpy arrays (distances in meters, durations in seconds)
            distances = np.array(data['distances']) / 1000.0  # Convert to kilometers
            durations = np.array(data['durations']) / 60.0    # Convert to minutes
            
            print(f"  ✓ Successfully retrieved {self.n_locations}x{self.n_locations} matrix")
            return distances, durations
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ OSRM API request failed: {e}")
            print("  Falling back to Haversine distance...")
            return self._fallback_haversine_matrix()
        except Exception as e:
            print(f"  ✗ Error processing OSRM response: {e}")
            print("  Falling back to Haversine distance...")
            return self._fallback_haversine_matrix()
    
    def _get_batched_matrix(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get matrix in batches for large datasets."""
        print(f"  Using batched requests (batch size: {batch_size})")
        
        distances = np.zeros((self.n_locations, self.n_locations))
        durations = np.zeros((self.n_locations, self.n_locations))
        
        # Process in smaller batches to avoid URL length limits
        for i in range(0, self.n_locations, batch_size):
            end_i = min(i + batch_size, self.n_locations)
            batch_locations = self.locations[i:end_i]
            
            print(f"    Processing batch {i//batch_size + 1}: locations {i} to {end_i-1}")
            
            # For each location in the batch, get distances to all other locations
            for j, (source_lat, source_lon) in enumerate(batch_locations):
                source_idx = i + j
                
                # Create smaller sub-batches for destinations to avoid URL length limits
                dest_batch_size = min(50, self.n_locations)  # Smaller destination batches
                
                for dest_start in range(0, self.n_locations, dest_batch_size):
                    dest_end = min(dest_start + dest_batch_size, self.n_locations)
                    dest_locations = self.locations[dest_start:dest_end]
                    
                    # Single source to multiple destinations
                    source_coord = f"{source_lon},{source_lat}"
                    dest_coords = ";".join([f"{lon},{lat}" for lat, lon in dest_locations])
                    
                    url = f"{self.osrm_server}/table/v1/driving/{source_coord}"
                    
                    params = {
                        'destinations': dest_coords,
                        'annotations': 'distance,duration'
                    }
                    
                    try:
                        response = requests.get(url, params=params, timeout=15)
                        response.raise_for_status()
                        data = response.json()
                        
                        if data['code'] == 'Ok':
                            batch_distances = np.array(data['distances'][0]) / 1000.0  # [0] for first source
                            batch_durations = np.array(data['durations'][0]) / 60.0
                            
                            distances[source_idx, dest_start:dest_end] = batch_distances
                            durations[source_idx, dest_start:dest_end] = batch_durations
                        else:
                            print(f"      ✗ Sub-batch failed for location {source_idx}: {data.get('message', 'Unknown error')}")
                            # Fill with Haversine distances
                            for k in range(len(dest_locations)):
                                dest_idx = dest_start + k
                                if source_idx != dest_idx:
                                    dist = self._haversine_distance(
                                        source_lat, source_lon,
                                        dest_locations[k][0], dest_locations[k][1]
                                    )
                                    distances[source_idx, dest_idx] = dist
                                    durations[source_idx, dest_idx] = dist / 0.5  # Assume 30 km/h
                        
                        time.sleep(0.05)  # Very short delay to be respectful
                        
                    except Exception as e:
                        print(f"      ✗ Request failed for location {source_idx}: {e}")
                        # Fill with Haversine distances for this sub-batch
                        for k in range(len(dest_locations)):
                            dest_idx = dest_start + k
                            if source_idx != dest_idx:
                                dist = self._haversine_distance(
                                    source_lat, source_lon,
                                    dest_locations[k][0], dest_locations[k][1]
                                )
                                distances[source_idx, dest_idx] = dist
                                durations[source_idx, dest_idx] = dist / 0.5  # Assume 30 km/h
        
        return distances, durations
    
    def _fallback_haversine_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """Fallback to Haversine distance calculation."""
        distances = np.zeros((self.n_locations, self.n_locations))
        durations = np.zeros((self.n_locations, self.n_locations))
        
        for i in range(self.n_locations):
            for j in range(self.n_locations):
                if i != j:
                    dist = self._haversine_distance(
                        self.locations[i][0], self.locations[i][1],
                        self.locations[j][0], self.locations[j][1]
                    )
                    distances[i, j] = dist
                    durations[i, j] = dist / 0.5  # Assume 30 km/h average speed
        
        return distances, durations
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def calculate_route_distance(self, route: List[int], use_duration: bool = False) -> float:
        """Calculate total distance or duration for a given route."""
        matrix = self.duration_matrix if use_duration else self.distance_matrix
        total = 0
        for i in range(len(route)):
            from_idx = route[i]
            to_idx = route[(i + 1) % len(route)]  # Return to start
            total += matrix[from_idx][to_idx]
        return total
    
    def nearest_neighbor_tsp(self, start_city: int = 0, use_duration: bool = False) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor heuristic with OSRM distances."""
        matrix = self.duration_matrix if use_duration else self.distance_matrix
        
        unvisited = set(range(self.n_locations))
        current_city = start_city
        route = [current_city]
        unvisited.remove(current_city)
        
        while unvisited:
            nearest_city = min(unvisited, key=lambda city: matrix[current_city][city])
            route.append(nearest_city)
            unvisited.remove(nearest_city)
            current_city = nearest_city
        
        return route, self.calculate_route_distance(route, use_duration)
    
    def two_opt_improvement(self, route: List[int], max_iterations: int = 1000, use_duration: bool = False) -> Tuple[List[int], float]:
        """Improve a route using 2-opt local search with OSRM distances."""
        best_route = route[:]
        best_distance = self.calculate_route_distance(best_route, use_duration)
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
                    
                    new_distance = self.calculate_route_distance(new_route, use_duration)
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
            
            route = best_route
        
        return best_route, best_distance
    
    def solve_tsp(self, use_duration: bool = False, max_starts: int = 10) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor + 2-opt improvement with OSRM."""
        if self.distance_matrix is None:
            self.distance_matrix, self.duration_matrix = self.get_osrm_matrix()
        
        print(f"\nSolving TSP using {'travel time' if use_duration else 'distance'} optimization...")
        
        # Try multiple starting points and pick the best
        best_route = None
        best_distance = float('inf')
        
        start_points = min(max_starts, self.n_locations)
        
        for start in range(start_points):
            print(f"  Trying starting point {start + 1}/{start_points}...")
            route, distance = self.nearest_neighbor_tsp(start, use_duration)
            improved_route, improved_distance = self.two_opt_improvement(route, use_duration=use_duration)
            
            if improved_distance < best_distance:
                best_distance = improved_distance
                best_route = improved_route
        
        return best_route, best_distance
    
    def save_route_to_csv(self, route: List[int], filename: str = 'osrm_optimized_route.csv', use_duration: bool = False):
        """Save the optimized route to a CSV file with OSRM data."""
        with open(filename, 'w', newline='') as file:
            import csv
            writer = csv.writer(file)
            
            headers = ['Order', 'LocationIndex', 'Latitude', 'Longitude', 'Distance_km', 'Duration_min']
            writer.writerow(headers)
            
            for i, location_idx in enumerate(route):
                lat, lon = self.locations[location_idx]
                next_idx = route[(i + 1) % len(route)]
                
                distance_km = self.distance_matrix[location_idx][next_idx]
                duration_min = self.duration_matrix[location_idx][next_idx]
                
                writer.writerow([i+1, location_idx, lat, lon, f"{distance_km:.3f}", f"{duration_min:.1f}"])
    
    def print_route_summary(self, route: List[int], distance: float, use_duration: bool = False):
        """Print a summary of the route with OSRM data."""
        unit = "minutes" if use_duration else "km"
        total_duration = self.calculate_route_distance(route, use_duration=True)
        total_distance = self.calculate_route_distance(route, use_duration=False)
        
        print(f"\n{'='*60}")
        print(f"OSRM TSP SOLUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Distance: {total_distance:.2f} km")
        print(f"Total Travel Time: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"Number of Locations: {len(route)}")
        print(f"Optimized for: {'Travel Time' if use_duration else 'Distance'}")
        print(f"Average speed: {total_distance / (total_duration/60):.1f} km/h")
        
        print(f"\nRoute Order: {' -> '.join(map(str, route[:10]))}", end="")
        if len(route) > 10:
            print(f" -> ... -> {route[0]} (return to start)")
        else:
            print(f" -> {route[0]} (return to start)")

def main():
    print("OSRM-based Water Meter TSP Solver")
    print("=" * 40)
    
    # Initialize OSRM TSP solver
    print("Loading water meter location data...")
    try:
        # You can change the OSRM server here
        # osrm = OSRMTSPSolver('Watermeterlocation.csv', 'http://localhost:5000')  # Local OSRM
        osrm = OSRMTSPSolver('Watermeterlocation.csv')  # Public OSRM server
    except FileNotFoundError:
        print("Error: Watermeterlocation.csv not found!")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print(f"Loaded {osrm.n_locations} water meter locations")
    
    # Ask user for optimization preference
    print("\nOptimization Options:")
    print("1. Minimize distance (km)")
    print("2. Minimize travel time (minutes)")
    
    while True:
        try:
            choice = int(input("Choose optimization method (1 or 2): "))
            if choice in [1, 2]:
                use_duration = choice == 2
                break
            else:
                print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number")
    
    # Solve TSP
    print(f"\nFetching real-world routing data and solving TSP...")
    start_time = time.time()
    best_route, best_value = osrm.solve_tsp(use_duration=use_duration)
    end_time = time.time()
    
    # Display results
    print(f"\nSolution found in {end_time - start_time:.2f} seconds")
    osrm.print_route_summary(best_route, best_value, use_duration)
    
    # Save results
    filename = f'osrm_route_{"time" if use_duration else "distance"}_optimized.csv'
    osrm.save_route_to_csv(best_route, filename, use_duration)
    print(f"\nOptimized route saved to '{filename}'")
    
    # Performance comparison
    if not use_duration:
        time_route, time_value = osrm.solve_tsp(use_duration=True)
        print(f"\nComparison:")
        print(f"  Distance-optimized: {best_value:.2f} km, {osrm.calculate_route_distance(best_route, True):.1f} min")
        print(f"  Time-optimized: {osrm.calculate_route_distance(time_route, False):.2f} km, {time_value:.1f} min")

if __name__ == "__main__":
    main()
