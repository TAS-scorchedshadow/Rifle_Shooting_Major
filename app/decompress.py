import json
import os
import tarfile
import zlib
import datetime

from app.models import Stage, User
from app.uploadProcessing import checkSighter


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


def read_archive():
    # Define file directory
    proj = os.path.dirname(os.path.realpath('__file__'))
    uploadDir = os.path.join(proj, 'app/static/tar')
    # Create a list of Stage IDs present in the database
    idList = [stage.id for stage in Stage.query.all()]
    userList = [user.username for user in User.query.all()]
    # Define list for return
    files_found = 0
    new_files = 0
    new_files_in_time = 0
    stageList = []
    # Files must be created earlier than 2yrs ago.
    lastDate = datetime.datetime.now() - datetime.timedelta(days=2*365)
    unixTime = (lastDate - datetime.datetime(1970,1,1)).total_seconds()*1000
    # Loop through the upload directory
    for filename in os.listdir(uploadDir):
        tar = tarfile.open(os.path.join(uploadDir, filename), "r:gz")
        # Loop through each member of the tgz file
        for member in tar.getmembers():
            name = member.name
            # Ensure that regular meta files are not computed
            if name[:9] == "./string-" and name[-4:] == ".zip":
                files_found += 1
                try:
                    id = int(name[9:-4]) # Removes './string-' prefix and '.zip' from string
                    # Check if the id already exists in the database
                    if id not in idList:
                        new_files += 1
                        data = json.loads(decompress_zlib(tar.extractfile(member).read()))
                        # Check if the file was made in the last 2 years
                        if data['ts'] > unixTime:
                            new_files_in_time += 1
                            # Issue code denotes issues with stages that will be manually addressed
                            # 1 Username was not found in database
                            # 2 3 Shots (Not including sighters) or less were found
                            # 3 Group information is missing from the target
                            # If there are no codes the file is ready for upload
                            issue_code = []
                            if data['name'] not in userList:
                                issue_code.append(1)
                            if num_shots(data) < 3:
                                issue_code.append(2)
                            if not ('stats_group_size' in data and 'stats_group_center' in data):
                                issue_code.append(3)        # todo Issue Code 3 is synonymous with Code 2
                            stageList.append((data, issue_code))
                except ValueError:
                    # In case out of format files were added to archive e.g. "./string-default-string.zip"
                    print('invalid filename skipped')

    print("Found {} files in archive".format(files_found))
    print("Found {} new files in archive".format(new_files))
    print("Found {} new relevant files in archive (Made in the last 2yrs)".format(new_files_in_time))

    return stageList


def num_shots(data):
    num = 0
    for individualShot in data['shots']:
        x = individualShot['valid']
        if x:
            if not checkSighter(individualShot):
                num += 1
    return num


def check_valid_group_info(data):
    if 'stats_group_size' in data and 'stats_group_center' in data:
        return True
    else:
        return False