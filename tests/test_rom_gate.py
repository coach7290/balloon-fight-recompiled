import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("prepare_rom", Path(__file__).resolve().parents[1] / "tools/prepare_rom.py")
rom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rom)


class RomGateTests(unittest.TestCase):
    def test_truncated_image_is_rejected(self):
        with self.assertRaises(ValueError):
            rom.validate(rom.HEADER)

    def test_correct_container_with_wrong_game_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Game data does not match"):
            rom.validate(rom.HEADER + bytes(24576))

    def test_trainer_flag_is_rejected(self):
        header = bytearray(rom.HEADER)
        header[6] = 4
        with self.assertRaisesRegex(ValueError, "no trainer"):
            rom.validate(header + bytes(24576))

    def test_nes2_extended_mapper_is_rejected(self):
        header = bytearray(rom.HEADER)
        header[7], header[8] = 8, 1
        with self.assertRaisesRegex(ValueError, "mapper/submapper"):
            rom.validate(header + bytes(24576))

    def test_ambiguous_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / "ambiguous.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("one.nes", b"x")
                z.writestr("two.nes", b"x")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                rom.read_input(archive)

    def test_zip_entry_is_read_without_extracting_its_path(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / "nested.zip"
            content = rom.HEADER + bytes(24576)
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../../not-extracted.nes", content)
            self.assertEqual(rom.read_input(archive), content)
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()), ["nested.zip"])


if __name__ == "__main__":
    unittest.main()
