import cv2
import numpy as np


def keypoint_matching(img, template, min_matches=10):
    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(img, None)

    if des1 is None or des2 is None:
        print("Descriptor computation failed.")
        return img

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    if len(matches) >= min_matches:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            print("Homography computation failed.")
            return img

        h, w = template.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        img_with_template = cv2.polylines(img.copy(), [np.int32(dst)], True, (0, 0, 0), 10, cv2.LINE_AA)
        return img_with_template
    else:
        print(f"Not enough matches are found - {len(matches)}/{min_matches}")
        return img
