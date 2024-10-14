import cv2

from algs.keypoint_mathcing import keypoint_matching
from algs.template_matching import template_matching

import matplotlib.pyplot as plt

from utils.show_image import show_image

if __name__ == "__main__":
    template_image_path = 'images/template.png'
    target_image_path = 'images/image2.png'

    template_img = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
    target_img = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)

    template_result = template_matching(target_img, template_img)
    keypoint_result = keypoint_matching(target_img, template_img)

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    show_image(plt, cv2.cvtColor(template_result, cv2.COLOR_BGR2RGB), 'Template Matching')

    plt.subplot(1, 3, 2)
    show_image(plt, cv2.cvtColor(template_img, cv2.COLOR_BGR2RGB), 'Template image')

    plt.subplot(1, 3, 3)
    show_image(plt, cv2.cvtColor(keypoint_result, cv2.COLOR_BGR2RGB), 'Keypoints Matching')

    plt.show()
