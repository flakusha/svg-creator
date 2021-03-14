# Just an example of image, you must pick image data as plain list of
# RGBA values from image data block
import random, time
import numpy as np

def pfl(flist, num, reverse = False, end = "\n"):
    """Print formatted list, accepts list of floats, number of elements to
    print and bool to print from the end of list."""
    if reverse:
        num = -num
        [print("{:3.3f}".format(i), end = " ") for i in flist[num:]]
    else:
        [print("{:3.3f}".format(i), end = " ") for i in flist[:num]]

    print(end, end = "")

# Source image size example, width * height * resolution upscale * channel num
so = 1920 * 1080 * 4 * 4 # [R, G, B, A, R, G, B, A, ...]

t = time.time()
image = [random.uniform(0, 1) for _ in range(so)]
tr = (time.time() - t)
print("{:4.3f} seconds: image creation".format(tr))

print("Debug: RGBA components:")
pfl(image, 4)
pfl(image, 4, True)
# exit()

# Remove Alpha values from bmp
t = time.time()
del image[3::4]
tr = (time.time() - t)
print("{:4.3f} seconds: alpha removal".format(tr))

print("Debug: first and last RGBs:")
pfl(image, 3)
pfl(image, 3, True)

# You can optionally convert to 0-100% range
# Separate list
t = time.time()
image_rgb = [x * 100 for x in image]
tr = (time.time() - t)
print("{:4.3f} seconds: new image in range 0-100%, list comp".format(tr))

# Lambda version
t = time.time()
image_rgb_l = list(map(lambda x: x * 100, image))
tr = (time.time() - t)
print("{:4.3f} seconds: new image in range 0-100%, lambda".format(tr))

# Numpy with conversion to 0-100% range
t = time.time()
image_np = list(np.array(image) * 100) # Remove list() to work with Numpy data
tr = (time.time() - t)
print("{:4.3f} seconds: new image in range 0-100%, Numpy".format(tr))

# In-place
t = time.time()
image[:] = [x * 100 for x in image]
tr = (time.time() - t)
print("{:4.3f} seconds: image in-place conversion in range 0-100%".format(tr))

# Now you can optionally convert image to list of RGB tuples
# Separate list creation
t = time.time()
image_rgb_t = list(zip(*[iter(image)] * 3))
tr = (time.time() - t)
print("{:4.3f} seconds: conversion to RGB tuples with new list creation"\
    .format(tr))

# In-place
t = time.time()
image[:] = zip(*[iter(image)] * 3)
tr = (time.time() - t)
print("{:4.3f} seconds: in-place RGB conversion".format(tr))

print("Debug: elements:")
print("Debug: image_rgb:", end = "\t")
pfl(image_rgb, 3, end = " ")
pfl(image_rgb, 3, True, end = " ")
print()
print("Debug: image_rgb_l:", end = "\t")
pfl(image_rgb_l, 3, end = " ")
pfl(image_rgb_l, 3, True, end = " ")
print()
print("Debug: image_np:", end = "\t")
pfl(image_np, 3, end = " ")
pfl(image_np, 3, True, end = " ")
print()
print("Debug: image_rgb_t:")
[print("{:3.3f}".format(e), end = " ") for e in image_rgb_t[0]]
print("", end = " ")
[print("{:3.3f}".format(e), end = " ") for e in image_rgb_t[-1]]
print()

# Now you have [(r, g, b), (r, g, b), ...] image.
# Comparison of tuples is much faster, because they are hashed,
# but you should consider list of lists structure in case you are
# planning to modify anything.

# I enjoy typing
