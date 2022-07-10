import os, re

from app import app
from app.common import settings, database

from fastapi import status
from fastapi.testclient import TestClient

# requests like object used to make API calls
client = TestClient(app)


# path to some sample files to be used for testing
sample_files_dir = os.path.join(os.path.dirname(__file__), "sample_files")
sample_image = os.path.join(sample_files_dir, "sample_image.jpg")
sample_document = os.path.join(sample_files_dir, "sample_document.pdf")
sample_music = os.path.join(sample_files_dir, "sample_music.mp3")

# reset the contents of the "database"
def reset_db():
    database.reset_database()


# assert if all the sample files exist
def test_sample_files_exist():
    assert os.path.exists(sample_image)
    assert os.path.isfile(sample_image)
    assert os.path.exists(sample_document)
    assert os.path.isfile(sample_document)
    assert os.path.exists(sample_music)
    assert os.path.isfile(sample_music)


# test the upload and download limit as specified in the DAILY_LIMIT_MB environment variable
def test_limit():
    reset_db()  # reset the database before running tests

    limit_bytes = settings.DAILY_LIMIT_MB * (1000 * 1000)

    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        image_bytes = image_file.read()
        document_bytes = document_file.read()
        music_bytes = music_file.read()

        # to be used as parameters when uploading the files
        file_params = [
            ("sample.jpg", image_bytes),
            ("sample.pdf", document_bytes),
            ("sample.mp3", music_bytes),
        ]

        used_size = 0
        while True:  # loop until the limit is reached; will continuously upload and download the sample files
            end = False
            for file_param in file_params:
                # upload a file
                response_upload = client.post("/files/", files={"file": file_param})
                upload_size = int(response_upload.request.headers["content-length"])
                used_size += upload_size

                if used_size >= limit_bytes:
                    # when the limit is reached, the API should return a 403 error
                    assert response_upload.status_code == status.HTTP_403_FORBIDDEN
                    end = True
                    break
                else:
                    response_upload_json = dict(response_upload.json())
                    assert response_upload.status_code == status.HTTP_200_OK
                    assert "privateKey" in response_upload_json.keys()
                    assert "publicKey" in response_upload_json.keys()

                    url = f"/files/{response_upload_json['publicKey']}"
                    response_download = client.get(url)
                    download_size = len(file_param[1])
                    used_size += download_size

                    if used_size >= limit_bytes:
                        assert response_download.status_code == status.HTTP_403_FORBIDDEN
                        end = True
                        break
                    else:
                        # if the limit still isn't reached, do a download of the uploaded file
                        content_disposition = response_download.headers["content-disposition"]
                        filename = re.findall('filename="(.+)"', content_disposition)[0]
                        filesize = len(response_download.content)

                        assert response_download.status_code == status.HTTP_200_OK
                        assert filename == file_param[0]
                        assert filesize == download_size

            if end:
                break


# test the upload API
def test_upload_file():
    reset_db()  # reset the database before running tests

    limit_bytes = settings.DAILY_LIMIT_MB * (1000 * 1000)

    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        image_bytes = image_file.read()
        document_bytes = document_file.read()
        music_bytes = music_file.read()

        total_filesize = len(image_bytes) + len(document_bytes) + len(music_bytes)

        assert total_filesize + 1000 < limit_bytes  # add extra kilobyte to make sure there's enough room to test

        file_params = [
            ("sample.jpg", image_bytes),
            ("sample.pdf", document_bytes),
            ("sample.mp3", music_bytes),
        ]

        for file_param in file_params:  # upload all the sample files
            response = client.post("/files/", files={"file": file_param})
            response_json = dict(response.json())

            # assert if the API return a successful status code and if it returns the public and private keys
            assert response.status_code == status.HTTP_200_OK
            assert "privateKey" in response_json.keys()
            assert "publicKey" in response_json.keys()


# test the download API
def test_download_file():
    reset_db()  # reset the database before running tests

    limit_bytes = settings.DAILY_LIMIT_MB * (1000 * 1000)

    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        image_bytes = image_file.read()
        document_bytes = document_file.read()
        music_bytes = music_file.read()

        total_filesize = len(image_bytes) + len(document_bytes) + len(music_bytes)
        # add extra kilobyte to make sure there's enough room to test; double for upload and download
        assert (total_filesize + 1000) * 2 < limit_bytes

        # for every file, check if the uploaded file is the same as the downloaded file
        # also check if the mime type is correct for that type of file

        files = {"file": ("sample.jpg", image_bytes)}
        response_image = client.post("/files/", files=files)
        response_image_json = dict(response_image.json())

        files = {"file": ("sample.pdf", document_bytes)}
        response_document = client.post("/files/", files=files)
        response_document_json = dict(response_document.json())

        files = {"file": ("sample.mp3", music_bytes)}
        response_music = client.post("/files/", files=files)
        response_music_json = dict(response_music.json())

        response_jsons = [response_image_json, response_document_json, response_music_json]
        for response_json in response_jsons:
            assert "privateKey" in response_json.keys()
            assert "publicKey" in response_json.keys()

        image_url = f"/files/{response_image_json['publicKey']}"
        document_url = f"/files/{response_document_json['publicKey']}"
        music_url = f"/files/{response_music_json['publicKey']}"

        response = client.get(image_url)
        content_type = response.headers["content-type"]
        content_disposition = response.headers["content-disposition"]
        filename = re.findall('filename="(.+)"', content_disposition)[0]
        filesize = len(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert filename == "sample.jpg"
        assert filesize == len(image_bytes)
        assert content_type == "image/jpeg"

        response = client.get(document_url)
        content_type = response.headers["content-type"]
        content_disposition = response.headers["content-disposition"]
        filename = re.findall('filename="(.+)"', content_disposition)[0]
        filesize = len(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert filename == "sample.pdf"
        assert filesize == len(document_bytes)
        assert content_type == "application/pdf"

        response = client.get(music_url)
        content_type = response.headers["content-type"]
        content_disposition = response.headers["content-disposition"]
        filename = re.findall('filename="(.+)"', content_disposition)[0]
        filesize = len(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert filename == "sample.mp3"
        assert filesize == len(music_bytes)
        assert content_type == "audio/mpeg"


# test the delete API
def test_delete_file():
    reset_db()

    limit_bytes = settings.DAILY_LIMIT_MB * (1000 * 1000)

    mode = "rb"
    with (
        open(sample_image, mode) as image_file,
        open(sample_document, mode) as document_file,
        open(sample_music, mode) as music_file,
    ):
        image_bytes = image_file.read()
        document_bytes = document_file.read()
        music_bytes = music_file.read()

        total_filesize = len(image_bytes) + len(document_bytes) + len(music_bytes)

        assert total_filesize + 1000 < limit_bytes  # add extra kilobyte to make sure there's enough room to test

        file_params = [
            ("sample.jpg", image_bytes),
            ("sample.pdf", document_bytes),
            ("sample.mp3", music_bytes),
        ]

        for file_param in file_params:  # loop through the sample files
            files = {"file": file_param}
            response = client.post("/files/", files=files)
            response_json = dict(response.json())

            # assert if the upload is successful
            assert response.status_code == status.HTTP_200_OK
            assert "publicKey" in response_json.keys()
            assert "privateKey" in response_json.keys()

            # use the private key to delete the file
            private_key = response_json["privateKey"]
            url = f"files/{private_key}"
            response = client.delete(url)
            assert response.status_code == status.HTTP_200_OK

            # if the file was successfully deleted, then calling another delete operation will return a 404 not found error
            response = client.delete(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND
