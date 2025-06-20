import pandas as pd
import numpy as np

from glob import glob
from tqdm.notebook import tqdm
from PIL import Image
import pytesseract

"""annotations = pd.read_parquet('.../Images/Screenshot 2025-06-17 134325.annotations.png')
images = pd.read_parquet('.../Images/Screenshot 2025-06-17 134325.image.png')
"""
"""images.head()"""

"""import easyocr as easy

reader = easy.ocr.Reader(['en'], gpu = False)

reader.readtext()"""

# Path to the image file
gray_image_path = 'Images/Screenshot 2025-06-17 134325.png'

# Open the image using PIL
image = Image.open(gray_image_path)

# Use pytesseract to do OCR on the image
text = pytesseract.image_to_string(image)

print('Extracted Text:')
print(text)