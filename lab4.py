import sys
import time
import torch
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from torch.autograd import Variable
from torchvision import transforms
from torchvision.models import resnet18
from torch2trt import torch2trt, TRTModule

# ImageNet - классы и ID
def class_dict_init(filepath: str):
    with open(filepath, 'r') as fd:
        return {int(line['class_id']): line['class_name'] for line in csv.DictReader(fd)}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

output_path = Path("./output")
output_path.mkdir(exist_ok=True)

# Обработка и классификация изображений
def batch_classify_images(images: list, model, class_dict: dict):
    print("Starting image processing...")
    timeimg = time.time()

    for image in images:
        index = classify_image(image, model)
        output_text = f"{index}: {class_dict[index]}"
        draw_and_save_image(image, output_text)

    print(f"Image processing time: {time.time() - timeimg:.2f} seconds")
    print(f'Memory allocated: {torch.cuda.memory_allocated()} bytes')

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# Классфикация одного изображения
def classify_image(image: Image, model) -> int:
    image_tensor = transform(image).unsqueeze(0).to(device)
    output = model(image_tensor)
    return output.data.cpu().numpy().argmax()

# Подпись с результатами, сохранение изображения
def draw_and_save_image(image: Image, output_text: str):
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, image.height - 20, image.width, image.height), fill=(255, 255, 255))
    draw.text((50, image.height - 15), output_text, fill=(0, 0, 0), font=ImageFont.load_default())
    image.save(output_path / Path(image.filename).name)

def main():
    # Проверка флага TensorRT
    trt_enabled = '-trt' in sys.argv
    if trt_enabled:
        sys.argv.remove('-trt')

    class_dict = class_dict_init('./imagenet/classes.csv')

    # Проверка и загрузка файлов из директории ./img
    img_dir = Path('./img')
    if not img_dir.exists() or not img_dir.is_dir():
        print(f"{img_dir} directory does not exist.")
        sys.exit(1)

    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    images = []
    for ext in image_extensions:
        images.extend(img_dir.glob(ext))

    image_list = []
    for img_path in images:
        try:
            image_list.append(Image.open(img_path))
        except FileNotFoundError:
            print(f"{img_path} not found")

    if not image_list:
        print(f"No images found in {img_dir}")
        sys.exit(1)

    # Загрузка модели
    load_time_start = time.time()

    model = resnet18(pretrained=True).eval().to(device)

    # TensorRT - оптимизация при наличии флага
    if trt_enabled:
        print("Optimizing model with TensorRT...")
        x = torch.ones((1, 3, 224, 224)).to(device)
        model_trt = torch2trt(model, [x])  # Оптимизация модели
        #torch.save(model_trt.state_dict(), 'resnet18_trt.pth')
        model = model_trt  # Use the optimized model
    else:
        print("Using regular ResNet18 model.")

    # Проверка наличия существующей TensorRT модели
    #try:
        #model_trt = TRTModule()
        #model_trt.load_state_dict(torch.load('resnet18_trt.pth'))  # Загрузка оптимизированной модели
        #model = model_trt
        #print("Loaded existing TensorRT model.")
    #except FileNotFoundError:
        #print("No existing TRT model found, proceeding with regular model.")

    load_time_end = time.time()
    print(f"Model load time: {load_time_end - load_time_start:.2f} seconds")

    # Обработка изображений
    batch_classify_images(image_list, model, class_dict)

if __name__ == "__main__":
    main()
