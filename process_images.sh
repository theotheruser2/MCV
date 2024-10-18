#!/bin/bash

# Path to the folder with the images
IMAGE_DIR="./img"

# Path to the compiled image_processing program
IMAGE_PROCESSING_BINARY="./image_processing"

# Path to the output folder for the processed images
OUTPUT_DIR="$IMAGE_DIR/processed_images"

# Create the output folder if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Output log file
OUTPUT_LOG="image_processing_output.txt"

# Clear the output log file at the start
> "$OUTPUT_LOG"

# Loop through all the files in the folder
for image in "$IMAGE_DIR"/*; do
    # Check if the image does not end with _gs
    if [[ "$image" != *_gs.* ]]; then
        # Extract the base name of the image without the extension
        base_name=$(basename "$image" | cut -f 1 -d '.')

        # Find the corresponding grayscale image
        grayscale_image="$IMAGE_DIR/${base_name}_gs.png"
        if [[ ! -f "$grayscale_image" ]]; then
            grayscale_image="$IMAGE_DIR/${base_name}_gs.jpg"
        fi

        # Check if the grayscale image exists
        if [[ -f "$grayscale_image" ]]; then
            # Log the process to the output file
            echo "Processing $image with $grayscale_image..." | tee -a "$OUTPUT_LOG"
            
            # Run the image_processing binary on the original image and its grayscale counterpart
            result_image_name="$OUTPUT_DIR/result_add_${base_name}_basic.png"
            "$IMAGE_PROCESSING_BINARY" "$image" "$grayscale_image" 2>&1 | tee -a "$OUTPUT_LOG"
        else
            # Log the missing grayscale image to the output file
            echo "Grayscale image for $image not found. Skipping..." | tee -a "$OUTPUT_LOG"
        fi
    fi
done

# Indicate that the process is complete
echo "Image processing complete. Results saved to $OUTPUT_LOG and in $OUTPUT_DIR."
