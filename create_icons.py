from PIL import Image, ImageDraw

icon_size = (32, 32)

icons = {
    'pet': [(10, 10), (22, 22), (16, 22), (12, 26), (20, 26)],
    'cat': [(8, 14), (24, 14), (12, 6), (20, 6), (16, 22), (10, 26), (22, 26)],
    'add': [(16, 6), (16, 26), (6, 16), (26, 16)],
    'alert': [(16, 4), (4, 28), (16, 20), (28, 28)],
    'stats': [(4, 24), (12, 16), (20, 8), (28, 24)],
    'needle': [(16, 4), (16, 28), (8, 20), (24, 20)],
    'settings': [(16, 8), (16, 24), (8, 16), (24, 16), (6, 6), (26, 6), (6, 26), (26, 26)]
}

for name, points in icons.items():
    img = Image.new('RGBA', icon_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon(points, fill=(255, 255, 255, 255))
    img.save(f'icons/{name}.png')

print("Icons created successfully!")