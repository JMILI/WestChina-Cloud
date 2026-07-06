import io
from typing import Callable, List, Optional, Tuple

import numpy as np
import pydicom
from minio import Minio
from pydicom.pixel_data_handlers.util import apply_modality_lut

from .config import settings
from .hu_utils import pixel_array_to_hu, slice_spacing_z


def _client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def _object_key(study_uid: str, series_uid: str, index_1based: int) -> str:
    return f"{study_uid}/{series_uid}/{index_1based}.dcm"


def download_series(
    bucket: str,
    study_uid: str,
    series_uid: str,
    image_count: int,
    on_slice: Optional[Callable[[int, int], None]] = None,
) -> List[bytes]:
    client = _client()
    payloads: List[bytes] = []
    for i in range(1, image_count + 1):
        key = _object_key(study_uid, series_uid, i)
        response = client.get_object(bucket, key)
        try:
            payloads.append(response.read())
        finally:
            response.close()
            response.release_conn()
        if on_slice:
            on_slice(i, image_count)
    return payloads


def download_slice(
    bucket: str,
    study_uid: str,
    series_uid: str,
    slice_index_0based: int,
) -> bytes:
    """下载单层 DICOM，slice_index 为 0-based，MinIO 文件名为 1-based。"""
    client = _client()
    key = _object_key(study_uid, series_uid, slice_index_0based + 1)
    response = client.get_object(bucket, key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def _to_hu(ds: pydicom.Dataset, arr: np.ndarray) -> np.ndarray:
    return pixel_array_to_hu(ds, arr)


def parse_slice(dicom_bytes: bytes) -> Tuple[np.ndarray, float, float, int, int, float]:
    """解析单层 DICOM，返回 HU、spacing_y、spacing_x、rows、cols、spacing_z(mm)。"""
    ds = pydicom.dcmread(io.BytesIO(dicom_bytes), force=True)
    arr = ds.pixel_array
    hu = pixel_array_to_hu(ds, arr)
    spacing_y, spacing_x = 1.0, 1.0
    ps = getattr(ds, "PixelSpacing", None)
    if ps is not None and len(ps) >= 2:
        spacing_y = float(ps[0])
        spacing_x = float(ps[1])
    rows, cols = hu.shape
    spacing_z = slice_spacing_z(ds)
    return hu.astype(np.float32), spacing_y, spacing_x, rows, cols, spacing_z


def build_volume(dicom_bytes_list: List[bytes]) -> Tuple[np.ndarray, Tuple[float, float, float], int, int]:
    """Return volume (Z,H,W) in HU, spacing (z,y,x) mm, rows, cols."""
    slices = []
    spacing_xy = (1.0, 1.0)
    spacing_z = 1.0

    for raw in dicom_bytes_list:
        ds = pydicom.dcmread(io.BytesIO(raw), force=True)
        arr = ds.pixel_array
        hu = _to_hu(ds, arr)
        slices.append(hu)

        ps = getattr(ds, "PixelSpacing", None)
        if ps is not None and len(ps) >= 2:
            spacing_xy = (float(ps[0]), float(ps[1]))

        st = getattr(ds, "SpacingBetweenSlices", None)
        if st is not None:
            spacing_z = float(st)
        else:
            st = getattr(ds, "SliceThickness", None)
            if st is not None:
                spacing_z = float(st)

    volume = np.stack(slices, axis=0).astype(np.float32)
    rows, cols = volume.shape[1], volume.shape[2]
    spacing = (spacing_z, spacing_xy[0], spacing_xy[1])
    return volume, spacing, rows, cols
