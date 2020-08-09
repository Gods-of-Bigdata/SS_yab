from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

from wordcloud_fa import WordCloudFa

def wordcloud_generator(text):
  mask_array = np.array(Image.open("iran_mask.png"))
  wodcloud = WordCloudFa(mask=mask_array, height=800, width=1200, persian_normalize=True, include_numbers=False, background_color="white")
  wc = wodcloud.generate(text)
  image = wc.to_image()
  image.save('wordcloud.png')