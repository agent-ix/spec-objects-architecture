import pytest

from spec_objects_architecture import MANIFEST_PATH, PACK_ROOT


@pytest.mark.trace("TC-001")
def test_manifest_path_points_to_packaged_manifest():
    assert MANIFEST_PATH == PACK_ROOT / "manifest.yaml"
    assert MANIFEST_PATH.is_file()
