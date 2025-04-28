from PIL import Image

# 1. List your nine image paths in row‑major order:
image_paths = [
    "traj_1.png",
    "traj_2.png",
    "traj_3.png",
    "traj_4.png",
    "traj_5.png",
    "traj_6.png",
    "traj_7.png",
    "traj_8.png",
    "traj_9.png",
]

# 2. Open all images and verify they’re the same size:
images = [Image.open(p) for p in image_paths]
widths, heights = zip(*(im.size for im in images))
if len(set(widths)) > 1 or len(set(heights)) > 1:
    raise ValueError("All images must have the same dimensions")

img_w, img_h = images[0].size

# 3. Create a new blank image of size (3×width, 3×height):
grid_w = img_w * 3
grid_h = img_h * 3
grid_img = Image.new(
    "RGBA", (grid_w, grid_h), (255, 255, 255, 0)
)  # transparent background

# 4. Paste each image into its spot:
for idx, im in enumerate(images):
    row = idx // 3
    col = idx % 3
    x = col * img_w
    y = row * img_h
    grid_img.paste(im, (x, y))

# 5. Save the result:
grid_img.save("grid_3x3.png")
