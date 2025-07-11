from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

def load_image_with_pillow(file_path):
    try:
        pil_img = Image.open(file_path).convert('RGBA')
        data = pil_img.tobytes('raw', 'RGBA')
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)
    except Exception as e:
        print(f'Pillow image load failed: {e}')
        return QPixmap() 