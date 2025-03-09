import numpy as np
import matplotlib.pyplot as plt
import os

# Function to apply lossy compression by zeroing out the least significant bits (LSBs) of the mantissa
def lossy_compress(data, bits_to_zero):
    """
    This function applies lossy compression by zeroing out the least significant bits
    of the mantissa of the floating-point numbers.

    Parameters:
    - data (np.array): The array of floating-point numbers to compress.
    - bits_to_zero (int): The number of least significant bits to zero out.

    Returns:
    - np.array: The compressed data as a float32 numpy array.
    """
    # Ensure the data is in float32 format
    data_fp32 = data.astype(np.float32)

    # View the float32 data as uint32 to manipulate the raw bits
    int_view = data_fp32.view(np.uint32)

    # Create a mask to zero out the desired number of least significant bits
    mask = np.uint32((1 << (32 - bits_to_zero)) - 1 << bits_to_zero)

    # Apply the mask to the integer view of the float data to zero out the LSBs
    int_view &= mask

    # Convert the compressed data back to float32 and return it
    return int_view.view(np.float32)


# Function to save data to a binary file
def save_binary(filename, data, dtype=np.float32):
    """
    Saves the given data to a binary file.

    Parameters:
    - filename (str): The name of the file where data will be saved.
    - data (np.array): The data to save.
    - dtype (np.dtype): The data type to convert the data to before saving.
    """
    data.astype(dtype).tofile(filename)


# Function to calculate the Mean Squared Error (MSE) between original and compressed data
def calculate_mse(original, compressed):
    """
    Calculates the Mean Squared Error (MSE) between the original and compressed data.

    Parameters:
    - original (np.array): The original uncompressed data.
    - compressed (np.array): The compressed data.

    Returns:
    - float: The MSE between the original and compressed data.
    """
    return np.mean((original - compressed) ** 2)


# Function to compare statistical properties (mean, variance, std dev) of original and compressed data
def compare_statistics(original, compressed, name):
    """
    Compares statistical properties (mean, variance, and standard deviation) of original and compressed data.

    Parameters:
    - original (np.array): The original data.
    - compressed (np.array): The compressed data.
    - name (str): The name of the distribution (for display purposes).
    """
    stats = {
        "Mean": (np.mean(original), np.mean(compressed)),
        "Variance": (np.var(original), np.var(compressed)),
        "Std Dev": (np.std(original), np.std(compressed))
    }
    print(f"\n{name} Distribution Statistics (Before vs. After Compression): {stats}")


# Generate 1,000,000 floating-point numbers from different distributions
n_samples = 1_000_000
uniform = np.random.uniform(-1, 1, n_samples).astype(np.float32)
gaussian = np.random.normal(0, 1, n_samples).astype(np.float32)
exponential = np.random.exponential(1, n_samples).astype(np.float32)

# Save original, full precision data
save_binary("uniform_original.bin", uniform)
save_binary("gaussian_original.bin", gaussian)
save_binary("exponential_original.bin", exponential)

# List of bit levels to test for compression (number of LSBs to zero out)
bit_levels = [8, 12, 16]

# Loop through different levels of compression
for bits_to_zero in bit_levels:
    print(f"\n### Compression with {bits_to_zero} bits zeroed ###")

    # Apply lossy compression to the datasets
    uniform_compressed = lossy_compress(uniform, bits_to_zero)
    gaussian_compressed = lossy_compress(gaussian, bits_to_zero)
    exponential_compressed = lossy_compress(exponential, bits_to_zero)

    # Save the compressed data as binary files
    save_binary(f"uniform_compressed_{bits_to_zero}bits.bin", uniform_compressed)
    save_binary(f"gaussian_compressed_{bits_to_zero}bits.bin", gaussian_compressed)
    save_binary(f"exponential_compressed_{bits_to_zero}bits.bin", exponential_compressed)

    # Compare file sizes before and after compression
    original_size_uniform = os.path.getsize("uniform_original.bin")
    compressed_size_uniform = os.path.getsize(f"uniform_compressed_{bits_to_zero}bits.bin")

    original_size_gaussian = os.path.getsize("gaussian_original.bin")
    compressed_size_gaussian = os.path.getsize(f"gaussian_compressed_{bits_to_zero}bits.bin")

    original_size_exponential = os.path.getsize("exponential_original.bin")
    compressed_size_exponential = os.path.getsize(f"exponential_compressed_{bits_to_zero}bits.bin")

    print(f"Original File Size (Uniform): {original_size_uniform} bytes")
    print(f"Compressed File Size (Uniform): {compressed_size_uniform} bytes")

    print(f"Original File Size (Gaussian): {original_size_gaussian} bytes")
    print(f"Compressed File Size (Gaussian): {compressed_size_gaussian} bytes")

    print(f"Original File Size (Exponential): {original_size_exponential} bytes")
    print(f"Compressed File Size (Exponential): {compressed_size_exponential} bytes")

    # Calculate and print MSE for each distribution
    mse_uniform = calculate_mse(uniform, uniform_compressed)
    mse_gaussian = calculate_mse(gaussian, gaussian_compressed)
    mse_exponential = calculate_mse(exponential, exponential_compressed)

    print(f"MSE (Uniform, {bits_to_zero} bits zeroed): {mse_uniform:.10f}")
    print(f"MSE (Gaussian, {bits_to_zero} bits zeroed): {mse_gaussian:.10f}")
    print(f"MSE (Exponential, {bits_to_zero} bits zeroed): {mse_exponential:.10f}")

    # Compare statistical properties before and after compression
    compare_statistics(uniform, uniform_compressed, "Uniform")
    compare_statistics(gaussian, gaussian_compressed, "Gaussian")
    compare_statistics(exponential, exponential_compressed, "Exponential")

# Plot the original vs. compressed distributions for each bit level
fig, axs = plt.subplots(3, len(bit_levels) + 1, figsize=(15, 12))

# Define distributions for plotting
distributions = [
    ("Uniform", uniform),
    ("Gaussian", gaussian),
    ("Exponential", exponential),
]

# Plot original distributions
for i, (name, orig) in enumerate(distributions):
    axs[i, 0].hist(orig, bins=100, alpha=0.7, label="Original", color="blue", density=True)
    axs[i, 0].set_title(f"Original {name} Distribution")
    axs[i, 0].set_xlabel("Value")
    axs[i, 0].set_ylabel("Density")
    axs[i, 0].legend()

# Plot compressed distributions for each bit level
for j, bits_to_zero in enumerate(bit_levels):
    uniform_compressed = lossy_compress(uniform, bits_to_zero)
    gaussian_compressed = lossy_compress(gaussian, bits_to_zero)
    exponential_compressed = lossy_compress(exponential, bits_to_zero)

    for i, (name, comp) in enumerate(zip(["Uniform", "Gaussian", "Exponential"],
                                          [uniform_compressed, gaussian_compressed, exponential_compressed])):
        axs[i, j + 1].hist(comp, bins=100, alpha=0.7, label=f"Compressed {bits_to_zero} bits", color="red", density=True)
        axs[i, j + 1].set_title(f"Compressed {name} ({bits_to_zero} bits)")
        axs[i, j + 1].set_xlabel("Value")
        axs[i, j + 1].set_ylabel("Density")
        axs[i, j + 1].legend()

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
