#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgcodecs.hpp"

#include <iostream>
#include <arm_neon.h>
#include <chrono>

using namespace std;
using namespace cv;

void add_images(const uint8_t* img1, const uint8_t* img2, uint8_t* result, int num_pixels) {
    for (int i = 0; i < num_pixels * 3; i++) {
        int sum = img1[i] + img2[i];
        result[i] = (sum > 255) ? 255 : sum;  // Cap at 255
    }
}

void subtract_images(const uint8_t* img1, const uint8_t* img2, uint8_t* result, int num_pixels) {
    for (int i = 0; i < num_pixels * 3; i++) {
        int diff = img1[i] - img2[i];
        result[i] = (diff < 0) ? 0 : diff;  // Floor at 0
    }
}

void add_images_neon(const uint8_t* img1, const uint8_t* img2, uint8_t* result, int num_pixels) {
    num_pixels *= 3; // Account for RGB channels
    int i = 0;
    for (; i <= num_pixels - 16; i += 16) {
        uint8x16_t a = vld1q_u8(img1 + i);
        uint8x16_t b = vld1q_u8(img2 + i);
        uint8x16_t sum = vqaddq_u8(a, b);  // Saturating addition (caps at 255)
        vst1q_u8(result + i, sum);
    }

    for (; i < num_pixels; i++) {
        int sum = img1[i] + img2[i];
        result[i] = (sum > 255) ? 255 : sum;
    }
}

void subtract_images_neon(const uint8_t* img1, const uint8_t* img2, uint8_t* result, int num_pixels) {
    num_pixels *= 3;
    int i = 0;
    for (; i <= num_pixels - 16; i += 16) {
        uint8x16_t a = vld1q_u8(img1 + i);
        uint8x16_t b = vld1q_u8(img2 + i);
        uint8x16_t diff = vqsubq_u8(a, b);  // Saturating subtraction (floors at 0)
        vst1q_u8(result + i, diff);
    }

    for (; i < num_pixels; i++) {
        int diff = img1[i] - img2[i];
        result[i] = (diff < 0) ? 0 : diff;
    }
}

string get_image_name(const string& path) {
    size_t last_slash_idx = path.find_last_of("\\/");
    if (last_slash_idx != string::npos) {
        return path.substr(last_slash_idx + 1);
    }
    return path;
}

string remove_extension(const string& filename) {
    size_t dot_idx = filename.find_last_of(".");
    if (dot_idx != string::npos) {
        return filename.substr(0, dot_idx);
    }
    return filename;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        cout << "Usage: program image1 image2" << endl;
        return -1;
    }

    Mat img1 = imread(argv[1], IMREAD_COLOR);
    Mat img2 = imread(argv[2], IMREAD_COLOR);
    if (!img1.data || !img2.data) {
        cout << "Could not open one of the images" << endl;
        return -1;
    }

    if (img1.size() != img2.size()) {
        cout << "Images must be the same size" << endl;
        return -1;
    }

    int num_pixels = img1.cols * img1.rows;
    uint8_t* img1_data = img1.data;
    uint8_t* img2_data = img2.data;

    Mat result_img(img1.rows, img1.cols, CV_8UC3);
    uint8_t* result_data = result_img.data;

    // Extract and print image1 name and size
    string image1_name = remove_extension(get_image_name(argv[1]));
    cout << "Processing Image: " << image1_name << endl;
    cout << "Image Size: " << img1.cols << " x " << img1.rows << endl;

    // Basic addition
    auto t1_basic_add = chrono::high_resolution_clock::now();
    add_images(img1_data, img2_data, result_data, num_pixels);
    auto t2_basic_add = chrono::high_resolution_clock::now();
    auto duration_basic_add = chrono::duration_cast<chrono::microseconds>(t2_basic_add - t1_basic_add).count();
    cout << "Basic addition took: " << duration_basic_add << " us" << endl;
    imwrite("result_add_" + image1_name + "_basic.png", result_img);

    // NEON addition
    auto t1_neon_add = chrono::high_resolution_clock::now();
    add_images_neon(img1_data, img2_data, result_data, num_pixels);
    auto t2_neon_add = chrono::high_resolution_clock::now();
    auto duration_neon_add = chrono::duration_cast<chrono::microseconds>(t2_neon_add - t1_neon_add).count();
    cout << "NEON addition took: " << duration_neon_add << " us" << endl;
    imwrite("result_add_" + image1_name + "_neon.png", result_img);

    // Basic subtraction
    auto t1_basic_sub = chrono::high_resolution_clock::now();
    subtract_images(img1_data, img2_data, result_data, num_pixels);
    auto t2_basic_sub = chrono::high_resolution_clock::now();
    auto duration_basic_sub = chrono::duration_cast<chrono::microseconds>(t2_basic_sub - t1_basic_sub).count();
    cout << "Basic subtraction took: " << duration_basic_sub << " us" << endl;
    imwrite("result_subtract_" + image1_name + "_basic.png", result_img);

    // NEON subtraction
    auto t1_neon_sub = chrono::high_resolution_clock::now();
    subtract_images_neon(img1_data, img2_data, result_data, num_pixels);
    auto t2_neon_sub = chrono::high_resolution_clock::now();
    auto duration_neon_sub = chrono::duration_cast<chrono::microseconds>(t2_neon_sub - t1_neon_sub).count();
    cout << "NEON subtraction took: " << duration_neon_sub << " us" << endl;
    imwrite("result_subtract_" + image1_name + "_neon.png", result_img);

    return 0;
}
