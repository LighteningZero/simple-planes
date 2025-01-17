# %%
import os
from os import walk
from os import listdir
from os.path import isfile, join
import cv2
import matplotlib.pyplot as plt
import numpy as np
from color_transfer import color_transfer
from shutil import copyfile

folder1 = r"../src/main/resources\data\simpleplanes\recipes"
# folder1 = r"../src/main/resources"
folder2 = "item"
base = "oak"
mat = "birch"
mod = "byg"
mod_short = "byg_"
mod_dict = {"bop": "biomesoplenty",
            "": "minecraft",
            "byg": "byg",
            "ft": "fruittrees"}



def get_rmp():
    return {
        r""""modid": "minecraft""""": fr""""modid": "{mod}""""",
        f"simpleplanes:{base}_plane": f"simpleplanes:{mod_short}{mat}_plane",
        f"simpleplanes:{base}_large_plane": f"simpleplanes:{mod_short}{mat}_large_plane",
        f"simpleplanes:{base}_mega_plane": f"simpleplanes:{mod_short}{mat}_mega_plane",
        f"simpleplanes:{base}_helicopter": f"simpleplanes:{mod_short}{mat}_helicopter",
        f"minecraft:{base}_boat": f"{mod}:{mat}_boat",
        f"item/{base}": f"item/{mod_short}{mat}",
        f"minecraft:{base}": f"{mod}:{mat}",
        f"{base}": mat
    }


f = []
for (dirpath, dirnames, filenames) in walk(folder1):
    f.extend(map(lambda f1: (dirpath, f1), filter(lambda f1: f"{base}" == f1[:3], filenames)))


def hsl_diff(origin):
    im1 = cv2.imread("oak.png")
    plt.imshow(cv2.cvtColor(im1, cv2.COLOR_BGRA2RGB))
    plt.title("oak")
    plt.show()

    im1 = cv2.cvtColor(im1, cv2.COLOR_BGRA2BGR)
    hsv1 = cv2.cvtColor(im1, cv2.COLOR_BGR2HLS)
    hchannel1 = hsv1[:, :, 0]
    im2 = cv2.imread(origin)
    plt.imshow(cv2.cvtColor(im2, cv2.COLOR_BGRA2RGB))
    plt.title("origin")
    plt.show()
    plt.imshow(cv2.cvtColor(color_transfer(im2, im1), cv2.COLOR_BGRA2RGB))
    plt.title("transfer")
    plt.show()

    im2 = cv2.cvtColor(im2, cv2.COLOR_BGRA2BGR)
    hsv2 = cv2.cvtColor(im2, cv2.COLOR_BGR2HLS)
    hchannel2 = hsv2[:, :, 0]
    h = np.average(hsv2, axis=(0, 1)) - np.average(hsv1, axis=(0, 1))
    return h


# print(f)
def gen(rmp, origin):
    # h = hsl_diff(origin)
    # im1 = cv2.imread("oak.png")
    # im1 = cv2.cvtColor(im1, cv2.COLOR_BGRA2BGR)
    #
    # print(h)
    # h = 0
    for dirpath, f1 in f:
        filename, file_extension = os.path.splitext(f1)
        path_join = os.path.join(dirpath, f1)
        if file_extension == ".json" and "mega_plane" in filename:
            replace = path_join.replace(base, f"{mod_short}{mat}")

            print("======", replace)
            with open(path_join, "r") as myfile:
                data = myfile.read()
            for k, v in rmp.items():
                data = data.replace(k, v)
            print(data)
            with open(replace, "w") as myfile:
                myfile.write(data)


def color_transfer(source, target, mask, target_mask):
    """
    Transfers the color distribution from the source to the target
    image using the mean and standard deviations of the L*a*b*
    color space.

    This implementation is (loosely) based on to the "Color Transfer
    between Images" paper by Reinhard et al., 2001.

    Parameters:
    -------
    source: NumPy array
        OpenCV image in BGR color space (the source image)
    target: NumPy array
        OpenCV image in BGR color space (the target image)

    Returns:
    -------
    transfer: NumPy array
        OpenCV image (w, h, 3) NumPy array (uint8)
    """
    # convert the images from the RGB to L*ab* color space, being
    # sure to utilizing the floating point data type (note: OpenCV
    # expects floats to be 32-bit, so use that instead of 64-bit)
    target1 = target.copy()
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    # compute color statistics for the source and target images
    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = image_stats(source, mask)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = image_stats(target, target_mask)
    print(lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc)
    print(lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar)

    # subtract the means from the target image
    (l, a, b) = cv2.split(target)
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar

    # scale by the standard deviations
    l = (lStdTar / lStdSrc) * l
    a = (aStdTar / aStdSrc) * a
    b = (bStdTar / bStdSrc) * b

    # add in the source mean
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc

    # clip the pixel intensities to [0, 255] if they fall outside
    # this range
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)

    # merge the channels together and convert back to the RGB color
    # space, being sure to utilize the 8-bit unsigned integer data
    # type
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)
    target1[target_mask] = transfer[target_mask]
    # return the color transferred image

    return target1


def image_stats(image, mask):
    """
    Parameters:
    -------
    image: NumPy array
        OpenCV image in L*a*b* color space

    Returns:
    -------
    Tuple of mean and standard deviations for the L*, a*, and b*
    channels, respectively
    """
    # compute the mean and standard deviation of each channel
    (l, a, b) = cv2.split(image)
    plt.show()
    (lMean, lStd) = (l[mask].mean(), l[mask].std())
    (aMean, aStd) = (a[mask].mean(), a[mask].std())
    (bMean, bStd) = (b[mask].mean(), b[mask].std())

    # return the color statistics
    return (lMean, lStd, aMean, aStd, bMean, bStd)


def im_color(mat):
    im1 = cv2.imread("item\\oak_large_plane.png")
    if mat == "oak":
        return
    # plt.imshow(cv2.cvtColor(im1, cv2.COLOR_BGRA2RGB))
    # plt.title("holly")
    # plt.show()

    im1 = cv2.cvtColor(im1, cv2.COLOR_BGRA2BGR)
    im2 = cv2.imread(f"item\\{mod_short}{mat}_large_plane.png")
    im2 = cv2.cvtColor(im2, cv2.COLOR_BGRA2BGR)

    eq1 = ~np.all(im1 == im2, axis=2)

    im_p1 = cv2.imread("mega\\bop_dead_mega_plane.png", cv2.IMREAD_UNCHANGED)
    src = im_p1
    im_p1 = cv2.cvtColor(im_p1, cv2.COLOR_BGRA2BGR)
    im_p2 = cv2.imread("mega\\oak_mega_plane.png", cv2.IMREAD_UNCHANGED)
    src = im_p2
    im_p2 = cv2.cvtColor(im_p2, cv2.COLOR_BGRA2BGR)
    eq2 = ~np.all(im_p1 == im_p2, axis=2)

    # im1[eq] = 0
    # im2[eq] = 0
    # plt.imshow(eq2.astype(int))
    # plt.title("eq2")
    # plt.show()

    # plt.imshow(cv2.cvtColor(im2, cv2.COLOR_BGRA2RGB))
    # plt.title(f"{mat}")
    # plt.show()
    im3 = color_transfer(im2, im_p1, eq1, eq2)
    # plt.imshow(cv2.cvtColor(im3, cv2.COLOR_BGRA2RGB))
    # plt.title("transfer")
    # plt.show()
    # plt.imshow(cv2.cvtColor(im_p1, cv2.COLOR_BGRA2RGB))
    # plt.title("oak plane")
    # plt.show()
    src[..., :-1] = im3
    src[src[..., -1] < 100] = 0
    plt.imshow(cv2.cvtColor(src, cv2.COLOR_BGRA2RGB))
    plt.title(f"{mat}_mega_plane.png")
    plt.show()
    cv2.imwrite(f"out/{mat}_mega_plane.png", src)




def recpie_list():
    for f1 in os.listdir("../src/main/resources/data/simpleplanes/recipes/"):
        if f1.endswith("json"):
            mat = f1[:-5]
            print(f""""simpleplanes:{mat}",""")


def recpie_to_fabric():
    path = "../src/main/resources/data/simpleplanes/recipes/"
    listdir = os.listdir(path)
    for f1 in listdir:
        path_join = os.path.join(path, f1)
        if os.path.isdir(path_join) or not f1.endswith(".json"):
            continue
        with open(path_join, "r") as myfile:
            data = myfile.read()
        mod = f1.split('_')[0]
        if mod.lower() not in ["bop", "ft", "byg"]:
            continue
        forge = ':mod_loaded'
        fabric = f"""{{
  "when": [
    {{
      "libcd:mod_loaded": "{mod}"
    }}
  ]
}}
"""
        if (forge in data):
            # data = data.replace(forge,fabric)
            print(data)
            with open(path_join + ".mcmeta", "w") as myfile:
                myfile.write(fabric)

            # break


def main():
    # recpie_to_fabric()
    # recpie_list()
    # im_color()
    # return
    global mat
    global mod_short
    global mod
    for f1 in os.listdir("../src/main/resources/assets/simpleplanes/textures/item"):
        mat = f1
        # print(f""""simpleplanes:{mat}",""")
        # continue

        if "_large_pl" not in mat:
            continue
        # if "byg" in mat:
        #     continue
        mat = mat.replace("_large_plane.png", "")
        # if "dark" not in mat:
        #     continue
        #     mat = mat.split("_")[1]
        Mat = mat.title()
        Mat = Mat.split('_')
        if Mat[0] in ["Bop", "Ft", "Byg"]:
            mod_short = Mat[0].lower()
            mod = mod_dict[mod_short]
            mod_short += "_"
            Mat = Mat[1:]
        else:
            mod = "minecraft"
            mod_short = ""
        # print(f""""mat:{mat}",mod:{mod}""")

        # Mat = " ".join(Mat)
        Mat = "_".join(Mat)
        mat = Mat.lower()
        # print(f"""
        # "item.simpleplanes.{mat}_plane": "{Mat} Plane",
        # "item.simpleplanes.{mat}_large_plane": "Large {Mat} Plane",
        # "item.simpleplanes.{mat}_helicopter": "{Mat} Helicopter",
        # "item.simpleplanes.{mat}_mega_plane": "{Mat} Cargo Plane",
        #         """)
        # continue
        # if mat!= "holly":
        #     continue
        print(f"(\"{mat}\"),")
        im_color(mat.lower())

        continue
        rmp = get_rmp()
        gen(rmp, os.path.join(folder2, f1))
        # break


if __name__ == '__main__':
    main()
