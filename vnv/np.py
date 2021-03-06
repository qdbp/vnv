import typing as ty
from functools import lru_cache

import numpy as np
from numpy.lib.stride_tricks import as_strided


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)


def decay(k, x, x0):
    return k * x + (1 - k) * x0


def complement_shape(shape: ty.Tuple[int, ...],
                     axis: int) -> ty.Tuple[int, ...]:
    if len(shape) < 1:
        raise ValueError("Cannot complement an empty shape.")

    return shape[:axis] + shape[axis + 1:]


def sl_window(arr: np.ndarray, window: int, stride: int, axis=0, sl_axis=0):
    """
    Generates staggered windows of an array.

    Given an array a of dimension N, stride size `stride`, and window size
    `window`, returns an array of dimension N + 1 of `window`-sized windows,
    each offset by `stride` from the previous. The 'sliding' happens along
    `axis` and the windows lie along `sl_axis` of the output array.

    Args:
        arr: array over which to generate windows
        window: window size
        stride: stride size
        axis: axis of `arr` along which to slide the window
        sl_axis: axis of output array along which windows will lie

    Returns:
        out: array of windows; shape nwindows on zeroth axis,
             w on axis corresponding to 'axis' argument, other
             dimensions unchanged
    """

    num_windows = 1 + (arr.shape[axis] - window) // stride
    win_stride = stride * arr.strides[axis]

    new_shape = arr.shape[:axis] + (window, ) + arr.shape[axis + 1:]
    new_shape = new_shape[:sl_axis] + (num_windows, ) + new_shape[sl_axis:]

    new_strides = arr.strides[:sl_axis] + (win_stride,
                                           ) + arr.strides[sl_axis:]

    return as_strided(arr, new_shape, new_strides)


def unsl_window(a):
    """
    Undoes the action of sl_window to the extent possible.
    """

    return a.base.base


def round_to_pow2(n):
    """
    Round a number to the next highest power of two.
    """
    return 2**np.ceil(np.log2(n))


@lru_cache(maxsize=4)
def hilbert_ixes(width):
    """
    Generates a mapping between the plane and the line.

    Assumes width is a power of 2.

    Returns:
        arr: ndarray such that arr[x, y] = hilbert_ix(x, y)
    """
    arr = np.zeros((width, width), dtype=np.uint64)

    proto = np.array([[0, 1], [3, 2]], dtype=np.uint64)
    arr[:2, :2] = proto[:]
    l = 2

    while len(proto) < width:

        arr[l:2 * l, :l] += proto.size + proto.T
        arr[l:2 * l, l:2 * l] = 2 * proto.size + proto.T
        arr[:l, l:2 * l] = 3 * proto.size + proto[::-1, ::-1]

        proto = arr[:l * 2, :l * 2].copy().T
        arr = arr.T
        l = len(proto)

    return arr
