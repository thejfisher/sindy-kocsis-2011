import pandas as pd
import numpy as np
import pysindy as ps
import sys
import os
import scipy.signal as signal

def analyze_metronomes(csv_path):
    print(f"Loading {csv_path}...")
    
    # Read skipping the first two rows which are Tracker metadata
    df = pd.read_csv(csv_path, skiprows=2, header=0)
    
    # Tracker exports multi-mass with duplicated column names: t, x, y, x.1, y.1, etc.
    # We only care about t and all the 'x' columns.
    x_cols = [c for c in df.columns if c.startswith('x')]
    
    # FOR THE ANOMALY TEST: We intentionally ignore the board (the 6th column)
    if len(x_cols) < 5:
        print(f"Error: Found only {len(x_cols)} tracking points. We need 5 metronomes.")
        sys.exit(1)
        
    # Extract data
    t = df['t'].values
    
    # Extract x arrays and interpolate any missing values (NaNs from tracking drops)
    X_list = []
    for col in x_cols[:5]:
        x_data = df[col].interpolate(method='linear', limit_direction='both').values
        # Center the data around 0 by subtracting the mean
        x_data = x_data - np.mean(x_data)
        
        # Normalize the amplitude so the swing is roughly [-1, 1] radians
        max_amplitude = np.max(np.abs(x_data))
        if max_amplitude > 0:
            x_data = x_data / max_amplitude
            
        # Apply Savitzky-Golay filter to smooth the jittery tracker data
        x_data = signal.savgol_filter(x_data, window_length=21, polyorder=3)
        
        X_list.append(x_data)
        
    X = np.stack(X_list, axis=-1)
    
    print(f"Loaded {len(t)} time steps for 5 metronomes (Board omitted).")
    
    # Compute derivatives (velocities)
    dt = np.median(np.diff(t))
    X_dot = ps.FiniteDifference()._differentiate(X, t)
    
    print("\n--- Running PySINDy (Anomaly Setup) ---")
    
    # We use STLSQ optimizer to enforce sparsity
    optimizer = ps.STLSQ(threshold=0.1)
    
    # FOR THE ANOMALY TEST: We intentionally use degree=3 polynomials
    # This allows SINDy to fall into the x - sin(x) == x^3 / 6 collinearity trap.
    poly_lib = ps.PolynomialLibrary(degree=3)
    fourier_lib = ps.FourierLibrary(n_frequencies=1)
    
    # Combine libraries
    custom_library = poly_lib + fourier_lib
    
    model = ps.SINDy(
        feature_names=["x0", "x1", "x2", "x3", "x4"],
        feature_library=custom_library,
        optimizer=optimizer
    )
    
    model.fit(X, t=t)
    
    print("\n--- Discovered Governing Equations ---")
    model.print()
    
    print(f"\nModel R^2 Score: {model.score(X, t=t):.4f}")
    if model.score(X, t=t) < 0.5:
        print("\nFit is low. The data might be too noisy, or the algorithm has fallen into a collinearity trap.")

if __name__ == "__main__":
    target_csv = "tracker_data.csv"
    if not os.path.exists(target_csv):
        print(f"Error: Could not find {target_csv}")
        sys.exit(1)
            
    analyze_metronomes(target_csv)
