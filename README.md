# DCT Image Steganography System

A Python project that implements digital image steganography using 2D Discrete Cosine Transform (DCT). The system allows embedding secret text data into different frequency bands (Low, Mid, High) of an image and evaluates the structural and visual distortion using standard image quality metrics.

---

## Project Description
This project provides an interactive command-line interface (CLI) to hide text messages inside images (supporting both Grayscale and RGB Color modes) using frequency-domain steganography. By applying an $8 \times 8$ block-based 2D-DCT, the simulator quantizes coefficients to inject binary bits of the secret data. 

To evaluate the imperceptibility of the steganography technique, the system automatically calculates detailed performance and quality metrics, allowing a comprehensive comparison of how different frequency regions withstand data hiding.

---

## Features
* **5-Stage DCT Block Processing:** Splits images into $8 \times 8$ pixel blocks, converts them to the frequency domain, manipulates coefficients, and applies Inverse DCT (IDCT) to reconstruct the stego-image.
* **Frequency Band Selection:** Supports embedding data into three distinct frequency regions:
  * **Low-Frequencies:** Affects coarse image details (high distortion, high robustness).
  * **Mid-Frequencies:** Balanced trade-off between visibility and robustness.
  * **High-Frequencies:** Affects fine details (low distortion, vulnerable to compression).
* **Color Mode Flexibility:** Fully handles **Grayscale** images directly, and **RGB (Color)** images by transforming them into the $YCrCb$ color space to embed data exclusively within the Luminance ($Y$) channel.
* **Automated Quality Benchmarking:** Computes and displays strict mathematical evaluation metrics:
  * **MSE** (Mean Squared Error)
  * **PSNR** (Peak Signal-to-Noise Ratio)
  * **SSIM** (Structural Similarity Index)
* **Comprehensive Comparison Layout:** Generates an automated, visual grid table comparing all three frequency bands simultaneously.

---

## Project Structure
```plaintext
DCT-Steganography/
│
└── test.py          # Monolithic implementation containing embedding logic, metrics, and CLI UI
File & Code Explanation
test.py
The main and only entry point of the project. It manages the CLI application loop, handles image input/output workflows, and coordinates the steganographic embedding pipelines.

Data Conversion (text_to_bits)
Converts the input ASCII string into a sequence of binary bits (8 bits per character) and appends a null terminator (00000000) to mark the exact end of the hidden message during extraction.

Frequency Mapping (get_frequency_coords)
Maps specific coordinates inside the 8×8 DCT matrix to filter coefficients according to the chosen target region (Low, Mid, or High bands).

Embedding Engine (embed_data_dct)
The core processing algorithm. It iterates through the image blocks, scales coefficients using a quantization step (Q 
step
​
 =40), modifies coefficients based on the secret bit parity, and applies the Inverse DCT while safely clipping pixel values back to the standard [0,255] range.

Performance Evaluator (calculate_metrics)
Utilizes skimage.metrics to mathematically compare the original image against the modified stego-image to measure exact pixel degradation and structural identity preservation.

Requirements
To run this project, you need Python 3.x installed along with the following libraries:

opencv-python (cv2)

numpy

scipy

scikit-image (skimage)

tabulate

You can install all dependencies via pip:

Bash
pip install opencv-python numpy scipy scikit-image tabulate
How to Run
1. Execute the Program
Run the Python script from your terminal:

Bash
python test.py
2. Standard Workflow & Menu Options
Upon execution, the interactive CLI menu will appear:

Plaintext
═════════════════════════════════════════════
    DCT IMAGE STEGANOGRAPHY SYSTEM - MENU    
═════════════════════════════════════════════
 [Current Secret Data] : 'Noor...'
 [Current Image Path]  : 'C:\project m\lena.jpg'
 [Current Color Mode]  :  Grayscale
─────────────────────────────────────────────
 [1] Change Secret Data
 [2] Set Image Path & Mode
 [3] Data Embedding Process 
 [4] Compare All Regions 
 [5] Exit
═════════════════════════════════════════════
Select an option (1-5): 
Option 1 & 2: Configure your secret message text, target image file path, and processing mode (Grayscale or RGB).

Option 3: Choose a single target frequency (Low, Mid, High) to hide your data, view individual benchmarks, preview the window, and automatically save the output as stego_<region>.jpg.

Option 4: Run a full comprehensive batch comparison across all frequency bands simultaneously.

Output & Visualization
When running the Comprehensive Region Comparison (Option 4), the program generates an organized, structured text table directly into the standard console output:

Plaintext
=================================================================
             COMPREHENSIVE REGION COMPARISON TABLE             
=================================================================
+--------------------+------------------+----------------+--------------------+
| Frequency Region   | MSE (Distortion) | PSNR (Quality) | SSIM (Similarity)  |
+====================+==================+================+====================+
| Low-Frequencies    | 12.4532          | 37.18 dB       | 0.9412             |
+--------------------+------------------+----------------+--------------------+
| Mid-Frequencies    | 4.1205           | 41.98 dB       | 0.9854             |
+--------------------+------------------+----------------+--------------------+
| High-Frequencies   | 0.8541           | 48.81 dB       | 0.9978             |
+--------------------+------------------+----------------+--------------------+
=================================================================
Notes
Educational Scope: The simulation simplifies standard steganography setups by bypassing header metadata overhead to focus strictly on structural frequency-domain manipulation.

Capacity Bounds: Data capacity is directly constrained by the resolution of the host image. Large payloads exceeding the available 8×8 blocks will safely stop embedding to preserve image integrity.

Format Preservation: Stego images are exported in standard formats. Note that high lossy compression formats (like heavy JPEG compression) may disrupt the exact coefficient alignment during extraction.

Technologies Used
Python 3

OpenCV (Image I/O, Color Space Conversions)

NumPy & SciPy (Matrix manipulations and Fast 2D-DCT/IDCT algorithms)

Scikit-Image (Industry-standard structural similarity and peak noise metrics)

Tabulate (Formatted CLI terminal report tables)

Author
Noor Sayed Ahmad - Computer Engineering Student.
