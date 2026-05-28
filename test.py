import os
import cv2
import numpy as np
from scipy.fftpack import dct, idct
from skimage.metrics import peak_signal_noise_ratio as psnr_metric
from skimage.metrics import structural_similarity as ssim_metric
from tabulate import tabulate

# Default Values
secret_data = "Noor"*200
image_path = r"C:\project m\lena.jpg"
image_mode = "Grayscale"  


def text_to_bits(text):
    #Convert a string text to binary 
    bits = []
    for char in text:
        bin_char = format(ord(char), '08b')#convert each character to ASCII -> 8-bit binary
        bits.extend([int(b) for b in bin_char])
    # add a null  (8 bits of 0) to know where the text ends 
    bits.extend([0] * 8)
    return bits

def apply_2d_dct(block):
    # DCT : 8x8 Block in Spatial Domain (Pixel values) -> 8x8 Block in Frequency Domain 
    return dct(dct(block.astype(float), axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_2d_idct(block):
    #Inverse DCT  Frequency Domain (Modified) -> Spatial Domain (pixel valuses)
    return idct(idct(block, axis=0, norm='ortho'), axis=1, norm='ortho')

def get_frequency_coords(region): 
  # Low, Mid, High frequency bands -> list ot tuples with the coordinates of the DCT  (خريطة للاماكن داخل block)
    
    if region == 'Low':
        # (top left of 8x8 block)
        return [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (2, 0)]
    elif region == 'Mid':
        return [(2, 2), (3, 1), (1, 3), (2, 3), (3, 2), (4, 1), (1, 4), (3, 3)]
    elif region == 'High':
        #(bottom right of 8x8 block)
        return [(6, 6), (7, 5), (5, 7), (6, 7), (7, 6), (7, 7), (6, 5), (5, 6)]
    return []

def embed_data_dct(img, text, region):
    bits = text_to_bits(text)
    bit_idx = 0
    num_bits = len(bits)
    
    stego_img = img.copy().astype(float)
    h, w = img.shape[:2]
    coords = get_frequency_coords(region)
    Q_step = 40 #
#divide image into 8x8 blocks
    for y in range(0, h - 7, 8):
        for x in range(0, w - 7, 8):
            #if secret has end then we stop to keep the image quality
            if bit_idx >= num_bits:
                break
            #convert block to Frequency Domain
            block = stego_img[y:y+8, x:x+8]
            dct_block = apply_2d_dct(block)
            #hide secret bits
            for coord in coords:
                if bit_idx < num_bits:
                    bit = bits[bit_idx]
                    coeff = dct_block[coord]
                    
                    quantized = int(np.round(coeff / Q_step))
                    if (quantized % 2) != bit:#-----------------
                        if quantized < 0:
                            quantized -= 1
                        else:
                            quantized += 1

                    dct_block[coord] = quantized * Q_step
                    bit_idx += 1
            
            stego_img[y:y+8, x:x+8] = apply_2d_idct(dct_block)
        if bit_idx >= num_bits:
            break

     #pixel values in the range [0, 255] 
    return np.clip(stego_img, 0, 255).astype(np.uint8)
   
def calculate_metrics(original, stego, mode):
    #Calculate MSE, PSNR, and SSIM between original and stego images.
    mse = np.mean((original.astype(float) - stego.astype(float)) ** 2)
    #if mse=0 -> original and stego images are exactly the same ->PSNR is infinite and SSIM is 1 (perfect similarity)
    if mse == 0:
        return 0, 100, 1.0
        
    psnr_val = psnr_metric(original, stego, data_range=255)
    
    # Calculate SSIM based on image mode
    if mode == "Grayscale":
        ssim_val = ssim_metric(original, stego, data_range=255)
    else:
        ssim_val = ssim_metric(original, stego, data_range=255, channel_axis=2)
        
    return mse, psnr_val, ssim_val

def load_image():
    if not os.path.exists(image_path):
        print(f"\n[ERROR] Image file not found at path: {image_path}")
        return None
        
    if image_mode == "Grayscale":
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        
    if img is None:
        print("\n[ERROR] Failed to decode image. Check file integrity.")
    return img

def process_single_region(region_name):
    #(Processes, displays metrics on console, and saves the output image file)
    img = load_image()
    if img is None:
        return
        
    print(f"\nEmbedding data into [{region_name}-frequencies]...")
    

    if image_mode == "Grayscale":
        stego_img = embed_data_dct(img, secret_data, region_name)
    else:
        ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y_channel, cr, cb = cv2.split(ycrcb_img)
        
        stego_y = embed_data_dct(y_channel, secret_data, region_name)
        
        stego_ycrcb = cv2.merge([stego_y, cr, cb])
        stego_img = cv2.cvtColor(stego_ycrcb, cv2.COLOR_YCrCb2BGR)
        
    mse, psnr_val, ssim_val = calculate_metrics(img, stego_img, image_mode)
    
    # Display Results
    print("\n" + "="*40)
    print(f" RESULTS FOR {region_name.upper()} FREQUENCIES ")
    print("="*40)
    print(f"Mean Squared Error (MSE)      : {mse:.4f}")
    print(f"Peak Signal-to-Noise Ratio 1   : {psnr_val:.2f} dB")
    print(f"Structural Similarity (SSIM)  : {ssim_val:.4f}")
    print("="*40)
    
    # Save output image
    output_filename = f"stego_{region_name.lower()}.jpg"
    cv2.imwrite(output_filename, stego_img)
    print(f"[ image saved as '{output_filename}' .")
    
    # Preview Image Window
    print("Press ANY KEY on the image window to close and continue.")
    cv2.imshow(f"Stego Image ({region_name} Freq)", stego_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_comprehensive_comparison():
    img = load_image()
    if img is None:
        return
        
    regions = ['Low', 'Mid', 'High']
    table_data = []
    
    print("\nProcessing comprehensive comparison across all bands. Please wait...")
    
    for r in regions:
        if image_mode == "Grayscale":
            stego_img = embed_data_dct(img, secret_data, r)
        else:
            ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            y_channel, cr, cb = cv2.split(ycrcb_img)
            stego_y = embed_data_dct(y_channel, secret_data, r)
            stego_ycrcb = cv2.merge([stego_y, cr, cb])
            stego_img = cv2.cvtColor(stego_ycrcb, cv2.COLOR_YCrCb2BGR)
            
        mse, psnr_val, ssim_val = calculate_metrics(img, stego_img, image_mode)
        table_data.append([f"{r}-Frequencies", f"{mse:.4f}", f"{psnr_val:.2f} dB", f"{ssim_val:.4f}"])
        
    # Print summary table
    headers = ["Frequency Region", "MSE (Distortion)", "PSNR (Quality)", "SSIM (Similarity)"]
    print("\n" + "=" * 65)
    print("             COMPREHENSIVE REGION COMPARISON TABLE             ")
    print("=" * 65)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("=" * 65 + "\n")


def main_menu():
    global secret_data, image_path, image_mode
    
    while True:
        print("\n" + "═"*45)
        print("    DCT IMAGE STEGANOGRAPHY SYSTEM - MENU    ")
        print("═"*45)
        print(f" [Current Secret Data] : '{secret_data}'")
        print(f" [Current Image Path]  : '{image_path}'")
        print(f" [Current Color Mode]  :  {image_mode}")
        print("─"*45)
        print(" [1] Change Secret Data")
        print(" [2] Set Image Path & Mode")
        print(" [3] Data Embedding Process ")
        print(" [4] Compare All Regions ")
        print(" [5] Exit")
        print("═"*45)
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            new_data = input(f"\nEnter new secret text: ").strip()
            if new_data:
                secret_data = new_data
                print("Secret updated successfully!")
            else:
                print("No change applied.")
                
        elif choice == '2':
            print(f"\nCurrent Image Path: {image_path}")
            new_path = input("Enter new image path (press Enter to keep current): ").strip()
            if new_path:
                # Strip potential quotation marks from copy-pasting paths
                image_path = new_path.strip('"').strip("'")
                
            print("\nSelect Image Processing Mode:")
            print(" 1. Grayscale ")
            print(" 2. RGB (Color)")
            mode_choice = input("Select choice (1 or 2): ").strip()
            if mode_choice == '2':
                image_mode = "RGB"
            else:
                image_mode = "Grayscale"
            print(f" Config updated. Path: '{image_path}' | Mode: {image_mode}")
            
        elif choice == '3':
            print("\n--- Select Target Frequency Region ---")
            print(" 1. Low-frequencies ")
            print(" 2. Mid-frequencies ")
            print(" 3. High-frequencies ")
            reg_choice = input("Select choice (1-3): ").strip()
            
            if reg_choice == '1':
                process_single_region('Low')
            elif reg_choice == '2':
                process_single_region('Mid')
            elif reg_choice == '3':
                process_single_region('High')
            else:
                print("Invalid choice.")
                
        elif choice == '4':
            run_comprehensive_comparison()
            
        elif choice == '5':
            print("\nExiting program.")
            break
        else:
              print("\n! Invalid choice. Try again.\n")


if __name__ == "__main__":
    # Start the Menu Loop
    main_menu()
