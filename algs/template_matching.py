import cv2


def template_matching(img, template):
    img_copy = img.copy()
    w, h = template.shape[:2]

    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(img_copy, top_left, bottom_right, (0, 0, 0), 10)

    return img_copy
