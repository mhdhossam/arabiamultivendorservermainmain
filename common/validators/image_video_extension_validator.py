from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
from django.utils.translation import gettext_lazy as _

allowed_extensions = ["jpg", "jpeg", "png", "mp4", "avi", "wav"]


def image_video_extension_validator(value):
    ext = get_valid_filename(value.name).split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _("Invalid file extension. Only JPG, JPEG, PNG, MP4, AVI and WAV files are allowed")
        )
