#!/bin/bash

# Paths to the images and their grayscale counterparts
IMAGES=(
    "Lenna.png"
    "tree.png"
    "Laptop_Big.jpg"
)

# Directory for the images
IMAGE_DIR="./img"

# Grayscale image suffix
GRAYSCALE_SUFFIX="_gs"

# Output folder for results
OUTPUT_DIR="$IMAGE_DIR/processed_images_opt"

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Source file for the image_processing binary
SOURCE_FILE="image_processing.cpp"

# Compiler options
COMPILER="g++"

# Optimization flags
OPTIMIZATION_FLAGS=("-O0" "-O1" "-O2" "-O3")

# Loop through the optimization levels
for OPT_FLAG in "${OPTIMIZATION_FLAGS[@]}"; do
    # Binary name for the current optimization level
    BINARY_NAME="image_processing_$OPT_FLAG"

    # Compile the binary with the current optimization flag
    echo "Compiling with $OPT_FLAG..."
    $COMPILER $SOURCE_FILE -o $BINARY_NAME $OPT_FLAG -I "/usr/include/opencv4" -L "/usr/lib/aarch64-linux-gnu" -lopencv_core -lopencv_highgui -lopencv_imgcodecs

    # Create a log file for this optimization level
    LOG_FILE="output_$OPT_FLAG.txt"
    > "$LOG_FILE"

    # Loop through each image and its corresponding grayscale image
    for IMAGE in "${IMAGES[@]}"; do
        # Extract the base name of the image
        BASE_NAME=$(basename "$IMAGE" | cut -f 1 -d '.')

        # Define the grayscale image path
        GRAYSCALE_IMAGE="$IMAGE_DIR/${BASE_NAME}${GRAYSCALE_SUFFIX}.png"
        if [[ ! -f "$GRAYSCALE_IMAGE" ]]; then
            GRAYSCALE_IMAGE="$IMAGE_DIR/${BASE_NAME}${GRAYSCALE_SUFFIX}.jpg"
        fi

        # Check if the grayscale image exists
        if [[ -f "$GRAYSCALE_IMAGE" ]]; then
            echo "Running $BINARY_NAME on $IMAGE and $GRAYSCALE_IMAGE..." | tee -a "$LOG_FILE"

            # Run the binary and append the results to the log file
            ./$BINARY_NAME "$IMAGE_DIR/$IMAGE" "$GRAYSCALE_IMAGE" 2>&1 | tee -a "$LOG_FILE"
        else
            echo "Grayscale image for $IMAGE not found. Skipping..." | tee -a "$LOG_FILE"
        fi
    done
done

echo "Processing complete. Logs saved for each optimization level."
