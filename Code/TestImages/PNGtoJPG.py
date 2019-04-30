from PIL import Image
from glob import glob

pngs = glob('./*.png')

for j in pngs:

    im = Image.open(j)

    im = Image.composite(im, Image.new('RGB', im.size, 'white'), im)

    im.save(j[:-3] + 'jpg',quality=100)
