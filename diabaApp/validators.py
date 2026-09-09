import re
from django.core import validators
from django.core.exceptions import ValidationError
from diabaApp import models


def validate_file_extension_video(self):
    """ This function is an amalgamation of two validations,
    file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv', '.3gp']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file with a '
                              'valid extension ie: mp4, mov, avi, or wmv')

    file_size = self.size

    if file_size > 52428800:  # 50MB
        raise ValidationError("The maximum file size that can be uploaded is 50MB")
    else:
        return self


def validate_file_extension_image(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp','.HEIF','.heic','.heif']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: jpg, jpeg, png, gif, webp ')

    file_size = self.size

    if file_size > 52428800:  # 1 MB
        raise ValidationError("File size should not be more than 1 MB.")
    else:
        return self


def validate_file_extension_image_and_video(self):
    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif','.mp4', '.mov', '.avi', '.wmv', '.mkv', '.3gp']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: jpg, jpeg, png, gif ')

    file_size = self.size

    if file_size > 52428800:  # 50MB
        raise ValidationError("The maximum file size that can be uploaded is 50MB")
    else:
        return self

def validate_file_extension_subtitle(self):
    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.srt']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: srt ')

    file_size = self.size

    if file_size > 52428800:  # 50MB
        raise ValidationError("The maximum file size that can be uploaded is 50MB")
    else:
        return self


def validate_file_extension_srt(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.srt']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: srt ')

    file_size = self.size

    if file_size > 1048576:  # 1 MB
        raise ValidationError("File size should not be more than 1 MB.")
    else:
        return self

def validate_file_extension_audio(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.mp3']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: mp3 ')

    file_size = self.size

    if file_size > 52428800:  # 1 MB
        raise ValidationError("File size should not be more than 50 MB.")
    else:
        return self



def validate_file_extension_pdf(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.pdf']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: mp3 ')

    file_size = self.size

    if file_size > 52428800:  # 1 MB
        raise ValidationError("File size should not be more than 50 MB.")
    else:
        return self