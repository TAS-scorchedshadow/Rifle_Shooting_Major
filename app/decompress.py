import json
import os
import tarfile
import zlib

from app.models import Stage


def decompress_all_zlib():
    proj = os.path.dirname(os.path.realpath('__file__'))
    uploadDir = os.path.join(proj, 'app/static/zlib_input')
    writeDir = os.path.join(proj, 'app/static/txt_output')
    for filename in os.listdir(uploadDir):
        print(filename)
        compressed_data = open(os.path.join(uploadDir, filename), 'rb').read()
        decompressed_data = zlib.decompress(compressed_data)
        decode = decompressed_data.decode("utf-8")
        destination = os.path.join(writeDir, filename[:-4] + ".txt")
        f = open(destination, "x")
        f.write(decode)
        f.close()


def decompress_zlib(file):
    decompressed_data = zlib.decompress(file)
    decoded = decompressed_data.decode("utf-8")
    return decoded


def tgz_reader():
    # Define file directory
    proj = os.path.dirname(os.path.realpath('__file__'))
    uploadDir = os.path.join(proj, 'app/static/tar')
    # Create a list of Stage IDs present in the database
    query = Stage.query.all()
    idList = [stage.id for stage in query]
    # Define list for return
    stageList = []
    # Loop through the upload directory
    for filename in os.listdir(uploadDir):
        tar = tarfile.open(os.path.join(uploadDir, filename), "r:gz")
        # Loop through each member of the tgz file
        for member in tar.getmembers():
            name = member.name
            # Ensure that meta files are not computed
            if name[-4:] == ".zip":
                id = name[9:-4]  # Removes './string-' prefix and '.zip' from string
                if id not in idList:
                    print(name)
                    decompressed_zlib = decompress_zlib(tar.extractfile(member).read())
                    obj = json.loads(decompressed_zlib)
                    stageList.append(obj)
    return stageList