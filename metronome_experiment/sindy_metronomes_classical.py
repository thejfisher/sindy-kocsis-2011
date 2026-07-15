"""
sindy_metronomes.py
===================
Analyzes the calibrated position data of 5 coupled metronomes.
Attempts to discover the governing kinetic phase-coupling equations using PySINDy.

Expects a CSV file with columns: t, x1, x2, x3, x4, x5
"""

import pandas as pd
import numpy as np
import pysindy as ps
import matplotlib.pyplot as plt
import os
import sys

def analyze_metronomes(csv_path):
    print(f"Loading {csv_path}...")
    
    # Read skipping the first two rows which are Tracker metadata
    # The actual columns are: t, x, y, x, y, x, y, x, y, x, y, (and trailing empty col)
    df = pd.read_csv(csv_path, skiprows=2, header=0)
    
    # Tracker exports multi-mass with duplicated column names: t, x, y, x.1, y.1, etc.
    # We only care about t and all the 'x' columns.
    x_cols = [c for c in df.columns if c.startswith('x')]
    
    if len(x_cols) < 6:
        print(f"Error: Found only {len(x_cols)} tracking points. We need 5 metronomes and 1 board.")
        sys.exit(1)
        
    # Extract data
    t = df['t'].values
    
    import scipy.signal as signal
    
    # Extract x arrays and interpolate any missing values (NaNs from tracking drops)
    X_list = []
    for col in x_cols[:6]:
        x_data = df[col].interpolate(method='linear', limit_direction='both').values
        # Center the data around 0 by subtracting the mean
        x_data = x_data - np.mean(x_data)
        
        # Normalize the amplitude so the swing is roughly [-1, 1] radians
        # (This is critical because sin(600 pixels) is meaningless noise)
        max_amplitude = np.max(np.abs(x_data))
        if max_amplitude > 0:
            x_data = x_data / max_amplitude
            
        # Apply Savitzky-Golay filter to smooth the jittery tracker data
        # window size 21, polynomial order 3
        x_data = signal.savgol_filter(x_data, window_length=21, polyorder=3)
        
        X_list.append(x_data)
        
    X = np.stack(X_list, axis=-1)
    
    print(f"Loaded {len(t)} time steps for 5 metronomes.")
    
    # ------------------------------------------------------------------
    # Custom Library: Polynomials + Sine of displacements
    # ------------------------------------------------------------------
    # In standard Kuramoto/TEGR, the coupling depends on the phase differences.
    # Here, displacement x is roughly proportional to phase for small angles.
    # So we include sin(x) as a potential basis function to see if the 
    # (x - sin(x)) structure emerges.
    
    print(f"Loaded {len(t)} time steps for 5 metronomes + 1 board.")
    
    # Compute derivatives (velocities)
    dt = np.median(np.diff(t))
    X_dot = ps.FiniteDifference()._differentiate(X, t)
    
    print("\n--- Running PySINDy ---")
    
    # We use STLSQ optimizer to enforce sparsity
    optimizer = ps.STLSQ(threshold=0.1)
    
    # Build library WITHOUT degree=3 polynomials to prevent the collinearity cheat
    poly_lib = ps.PolynomialLibrary(degree=2)
    fourier_lib = ps.FourierLibrary(n_frequencies=1)
    
    # Combine libraries
    custom_library = poly_lib + fourier_lib
    
    model = ps.SINDy(
        feature_library=custom_library,
        optimizer=optimizer
    )
    
    model.fit(X, t=t)
    
    print("\n--- Discovered Governing Equations ---")
    model.print()
    
    # Calculate R^2 score
    score = model.score(X, t=t)
    print(f"\nModel R^2 Score: {score:.4f}")
    
    if score > 0.95:
        print("\nExcellent fit! The macroscopic coupling was successfully captured.")
    else:
        print("\nFit is low. The data might be too noisy, or the time vector is incorrectly scaled.")

if __name__ == "__main__":
    target_csv = "tracker_data.csv"
    if not os.path.exists(target_csv):
        print(f"Error: Could not find {target_csv}")
        sys.exit(1)
            
    analyze_metronomes(target_csv)
