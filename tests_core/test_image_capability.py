import tempfile
import unittest
from pathlib import Path
from specforge.applications import get_application

class ImageCapabilityTests(unittest.TestCase):
    def test_missing_template_capability_fails_before_adaptation(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)
            with self.assertRaisesRegex(ValueError,"template ImageValidationService"):
                get_application("recipe-management").emit(source)
            self.assertEqual(list(source.iterdir()), [])

    def test_missing_frontend_upload_capability_fails_before_adaptation(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)
            image=source/'backend/src/main/java/com/original/system/file/service/ImageValidationService.java'
            image.parent.mkdir(parents=True);image.write_text('fixture')
            with self.assertRaisesRegex(ValueError,"template useFileUpload"):
                get_application("recipe-management").emit(source)
            self.assertFalse((source/'specforge/adaptations').exists())
