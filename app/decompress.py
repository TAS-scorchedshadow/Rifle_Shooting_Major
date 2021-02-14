import os
import zlib


def decompress_zlib():
    proj = os.path.dirname(os.path.realpath('__file__'))
    uploadDir = os.path.join(proj, 'app/static/zlib_input')
    writeDir = os.path.join(proj, 'app/static/txt_output')
    for filename in os.listdir(uploadDir):
        print(filename)
        compressed_data = open(os.path.join(uploadDir, filename), 'rb').read()
        decompressed_data = zlib.decompress(compressed_data)
        decode = decompressed_data.decode("utf-8")
        destination = os.path.join(writeDir, filename[:-4] +".txt")
        f = open(destination,"x")
        f.write(decode)
        f.close()