import logging
import os
import shutil

from fastapi import UploadFile

logger = logging.getLogger(__name__)


async def save_image(
    image_object: UploadFile,
    folder: str,
    path: str,
    name: str = 'logo',
    cleaning: bool = True
):
    directory = f"{path}/{folder}"

    if cleaning:
        await del_directory(directory=directory)

    os.makedirs(directory, exist_ok=True)  # Создаем директорию, если она не существует

    extension = os.path.splitext(image_object.filename)[1]
    new_file_name = f"{name}{extension}"
    file_path = os.path.join(directory, new_file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image_object.file, buffer)
        logger.info("Writing file: %r" % image_object.file)

    return file_path


async def del_directory(
    folder: str = '',
    path: str = '',
    directory: str = None
):
    if not directory:
        directory = f"{path}/{folder}"

    if os.path.exists(directory):                                          # Очищаем директорию, если она существует
        logger.info("Cleaning folder: %r" % directory)
        shutil.rmtree(directory)
