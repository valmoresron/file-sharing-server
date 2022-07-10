import os

from fastapi import UploadFile
from app.common import settings
from app.utils import FileUploadHandler, SavedFilesHandler

# path to some sample files to be used for testing
sample_files_dir = os.path.join(os.path.dirname(__file__), "sample_files")
sample_image = os.path.join(sample_files_dir, "sample_image.jpg")
sample_document = os.path.join(sample_files_dir, "sample_document.pdf")
sample_music = os.path.join(sample_files_dir, "sample_music.mp3")

upload_dir = settings.FOLDER  # where all the uploaded files are stored


# test if all the sample files exist
def test_sample_files_exist():
    assert os.path.exists(sample_image)
    assert os.path.isfile(sample_image)
    assert os.path.exists(sample_document)
    assert os.path.isfile(sample_document)
    assert os.path.exists(sample_music)
    assert os.path.isfile(sample_music)


# test the component responsible for handling uploaded files
def test_file_upload_handler():
    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        files = [
            ("sample.jpg", image_file),
            ("sample.pdf", document_file),
            ("sample.mp3", music_file),
        ]

        for filename, file in files:  # loop through the sample files
            upload_file = UploadFile(file=file, filename=filename)
            upload_handler = FileUploadHandler(upload_file)
            public_key = upload_handler.public_key
            private_key = upload_handler.private_key

            # public and private keys are always 64 characters long
            assert len(public_key) == 64
            assert len(private_key) == 64

            upload_handler.save_file()
            saved_filename = public_key + filename
            saved_filepath = os.path.join(upload_dir, saved_filename)

            # check if the file is successfully saved
            assert os.path.exists(saved_filepath) and os.path.isfile(saved_filepath)

            # check if the saved file matches the contents of the uploaded file
            with open(saved_filepath, mode) as saved_file:
                assert len(upload_handler.file_contents) == len(saved_file.read())


def test_saved_files_handler():
    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        files = [
            ("sample.jpg", image_file),
            ("sample.pdf", document_file),
            ("sample.mp3", music_file),
        ]

        files_handler = SavedFilesHandler()
        for filename, file in files:  # loop through the sample files
            files_handler.clean_up_files()  # clean up all the files inside the upload directory

            upload_file = UploadFile(file=file, filename=filename)
            upload_handler = FileUploadHandler(upload_file)
            public_key = upload_handler.public_key
            private_key = upload_handler.private_key

            # do a file upload
            upload_handler.save_file()
            saved_filename = public_key + filename
            saved_filepath = os.path.join(upload_dir, saved_filename)

            saved_filenames = files_handler.get_saved_filenames()
            saved_filepath_pub_key = files_handler.get_filepath_using_public_key(public_key)
            saved_filename_priv_key = files_handler.get_filename_using_private_key(private_key)
            original_filename = files_handler.get_original_filename(saved_filepath_pub_key)
            filesize = files_handler.get_file_size(saved_filepath)

            # check the saved files handler's functionalities
            assert saved_filename in saved_filenames
            assert saved_filepath == saved_filepath_pub_key
            assert saved_filename == saved_filename_priv_key
            assert original_filename == filename
            assert filesize == len(upload_handler.file_contents)

            assert os.path.exists(saved_filepath) and os.path.isfile(saved_filepath)
            files_handler.delete_saved_file(saved_filename)  # check if deleting a file works
            assert not os.path.exists(saved_filepath)

        files_handler.clean_up_files()
        assert len(files_handler.get_saved_filenames()) == 0

        # upload the sample files again without deleting
        for filename, file in files:
            upload_file = UploadFile(file=file, filename=filename)
            upload_handler = FileUploadHandler(upload_file)
            upload_handler.save_file()

        # check if the number of uploaded files matches the number of saved files
        assert len(files_handler.get_saved_filenames()) == len(files)

        # do a final clean up
        files_handler.clean_up_files()
