"""pytest: robust_ct_loader 单元测试。"""
import io
import struct

import numpy as np
import pydicom

from app.robust_ct_loader import (
    VolumeMeta,
    _get_ipp,
    _is_localizer,
    _extract_spacing,
    filter_localizer,
    load_series_dicoms,
    sort_by_ipp,
)


def _make_fake_dicom(ipp_z=0.0, instance_number=1, image_type=None, rows=64, cols=64):
    """构造最小可解析 DICOM dataset。"""
    ds = pydicom.Dataset()
    ds.ImagePositionPatient = [0.0, 0.0, ipp_z]
    ds.InstanceNumber = instance_number
    ds.Rows = rows
    ds.Columns = cols
    ds.PixelSpacing = [0.5, 0.5]
    ds.SliceThickness = 1.25
    ds.RescaleSlope = 1
    ds.RescaleIntercept = -1024
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.PixelData = np.zeros((rows, cols), dtype=np.uint16).tobytes()
    if image_type:
        ds.ImageType = image_type
    return ds


def _to_bytes(ds):
    """将 pydicom Dataset 序列化为 DICOM 字节流。"""
    from pydicom.uid import ImplicitVRLittleEndian, generate_uid
    ds.ensure_file_meta()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPClassUID = generate_uid()
    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
    ds.is_implicit_VR = True
    ds.is_little_endian = True
    buffer = io.BytesIO()
    pydicom.dcmwrite(buffer, ds, write_like_original=False)
    return buffer.getvalue()


class TestFilterLocalizer:
    def test_normal_ct_passes(self):
        ds = _make_fake_dicom(image_type=["ORIGINAL", "PRIMARY", "AXIAL"])
        kept, removed = filter_localizer([ds])
        assert len(kept) == 1
        assert removed == 0

    def test_localizer_filtered(self):
        ds = _make_fake_dicom(image_type=["ORIGINAL", "PRIMARY", "LOCALIZER"])
        kept, removed = filter_localizer([ds])
        assert len(kept) == 0
        assert removed == 1

    def test_scout_filtered(self):
        ds = _make_fake_dicom(image_type=["ORIGINAL", "PRIMARY", "SCOUT"])
        kept, removed = filter_localizer([ds])
        assert len(kept) == 0
        assert removed == 1


class TestSortByIPP:
    def test_ipp_sorting(self):
        ds1 = _make_fake_dicom(ipp_z=10.0, instance_number=3)
        ds2 = _make_fake_dicom(ipp_z=5.0, instance_number=1)
        ds3 = _make_fake_dicom(ipp_z=15.0, instance_number=2)
        sorted_ds, method = sort_by_ipp([ds1, ds2, ds3])
        assert method == "ipp"
        z_vals = [_get_ipp(d)[2] for d in sorted_ds]
        assert z_vals == [5.0, 10.0, 15.0]

    def test_fallback_to_instance_number(self):
        # No IPP → fallback to InstanceNumber
        ds1 = pydicom.Dataset()
        ds1.InstanceNumber = 3
        ds2 = pydicom.Dataset()
        ds2.InstanceNumber = 1
        sorted_ds, method = sort_by_ipp([ds1, ds2])
        assert method == "instance_number"
        assert sorted_ds[0].InstanceNumber == 1


class TestExtractSpacing:
    def test_spacing_from_tags(self):
        ds = _make_fake_dicom()
        spacing = _extract_spacing([ds])
        assert spacing == (1.25, 0.5, 0.5)

    def test_z_spacing_from_ipp(self):
        ds1 = _make_fake_dicom(ipp_z=0.0)
        ds2 = _make_fake_dicom(ipp_z=10.0)
        spacing = _extract_spacing([ds1, ds2])
        assert spacing[0] == 10.0  # z spacing


class TestLoadSeries:
    def test_volume_shape(self):
        dss = [_make_fake_dicom(ipp_z=i, instance_number=i, rows=32, cols=32) for i in range(3)]
        raw_list = [_to_bytes(d) for d in dss]
        meta = load_series_dicoms(raw_list)
        assert meta.volume.shape == (3, 32, 32)
        assert meta.slice_count == 3
        assert meta.sort_method == "ipp"

    def test_localizer_removed(self):
        dss = [
            _make_fake_dicom(ipp_z=0, instance_number=1, image_type=["LOCALIZER"]),
            _make_fake_dicom(ipp_z=1, instance_number=2),
            _make_fake_dicom(ipp_z=2, instance_number=3),
        ]
        raw_list = [_to_bytes(d) for d in dss]
        meta = load_series_dicoms(raw_list)
        assert meta.slice_count == 2
        assert meta.removed_localizers == 1
        assert meta.volume.shape[0] == 2
