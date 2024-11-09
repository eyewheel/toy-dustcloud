import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import sys

def analyze_digraphs(binary_data, log_scale=True, exclude_digraphs=None, vmax=None, min_threshold=None):
    """
    Analyze digraphs in binary data and create a heatmap visualization.
    
    Parameters:
        binary_data (bytes): Binary data to analyze
        log_scale (bool): Whether to use logarithmic scaling for the heatmap
        exclude_digraphs (list): List of digraphs to exclude (e.g. [('0', '0')])
        vmax (float): Maximum value for color scaling (useful for comparing multiple files)
        min_threshold (int): Minimum count to display (helps filter noise)
    """
    # Convert binary data to hex string
    hex_string = ''.join(f'{b:02X}' for b in binary_data)
    
    # Get all digraphs using numpy's striding tricks for efficiency
    hex_array = np.array(list(hex_string))
    digraphs = np.lib.stride_tricks.sliding_window_view(hex_array, 2)
    
    # Count digraphs using Counter
    digraph_counts = Counter(map(tuple, digraphs))
    
    # Create a 16x16 matrix for all possible hex digit combinations
    hex_digits = '0123456789ABCDEF'
    matrix = np.zeros((16, 16), dtype=float)  # Changed to float for log scaling
    
    # Fill the matrix with counts
    for (first, second), count in digraph_counts.items():
        if exclude_digraphs and (first, second) in exclude_digraphs:
            continue
        if min_threshold and count < min_threshold:
            continue
        i = hex_digits.index(first)
        j = hex_digits.index(second)
        matrix[i, j] = count
    
    # Apply log scaling if requested
    if log_scale and matrix.max() > 0:
        # Add 1 before taking log to handle zeros, then subtract 1 to keep zeros at 0
        matrix = np.where(matrix > 0, np.log1p(matrix), 0)
    
    # Create the visualization
    plt.figure(figsize=(12, 10))
    
    # Create heatmap with optional maximum value
    im = plt.imshow(matrix, cmap='viridis', vmax=vmax)
    plt.colorbar(im, label='Frequency (log scale)' if log_scale else 'Frequency')
    
    # Set up the axes with hex digits
    plt.xticks(range(16), list(hex_digits))
    plt.yticks(range(16), list(hex_digits))
    plt.xlabel('Second Digit')
    plt.ylabel('First Digit')
    
    # Create title based on settings
    title = 'Hexadecimal Digraph Frequency Heatmap\n'
    if log_scale:
        title += '(Log Scale) '
    if exclude_digraphs:
        title += f'(Excluding {", ".join(f"{a}{b}" for a,b in exclude_digraphs)}) '
    if min_threshold:
        title += f'(Min Count: {min_threshold})'
    plt.title(title)
    
    # Add text annotations for non-zero values
    for i in range(16):
        for j in range(16):
            if matrix[i, j] > 0:
                # Show original count (not log-scaled) in text
                original_value = np.expm1(matrix[i, j]) if log_scale else matrix[i, j]
                plt.text(j, i, f'{int(original_value)}', 
                        ha='center', va='center',
                        color='white' if matrix[i, j] > matrix.max()/2 else 'black',
                        fontsize=8)
    
    return matrix, digraph_counts

# Example usage
if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as f:
        binary_data = f.read()
    
    # Create multiple visualizations to compare
    """
    plt.figure(figsize=(15, 5))
  
    plt.subplot(131)
    analyze_digraphs(binary_data, log_scale=False)
    plt.title('Regular Scale')
    
    plt.subplot(132)
    analyze_digraphs(binary_data, log_scale=True)
    plt.title('Log Scale')
    
    plt.subplot(133)
    """
    analyze_digraphs(binary_data, log_scale=False, 
                    exclude_digraphs=[('0', '0')],
                    min_threshold=5)
    plt.title(sys.argv[1] + '\n(Excluding 00, Min Count: 5)')
    
    plt.tight_layout()
    plt.show()

