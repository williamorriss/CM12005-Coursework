import numpy as np
from PIL.Image import Image


def rms_img_diff(x: Image, y: Image) -> float:
    xs = np.array(x)
    ys = np.array(y)
    assert xs.shape == ys.shape
    return float(np.sqrt(np.mean((xs - ys) ** 2)))
