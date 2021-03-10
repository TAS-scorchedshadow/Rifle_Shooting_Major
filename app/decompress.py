import json
import os
import tarfile
import time
import zlib
import datetime
from math import floor

from app import app
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


@app.route('/archive')
def read_archive(uploaded, weeks):
    start = time.time()
    # Create a list of Stage IDs present in the database
    idList = [stage.id for stage in Stage.query.all()]
    userList = [user.username for user in User.query.all()]

    # Define some counters for print statements
    files_found = 0
    new_files = 0
    new_files_in_time = 0
    stageList = []

    # lastDate is the last accepted date in dattime. unixTime is the representation of that
    lastDate = datetime.datetime.now() - datetime.timedelta(weeks=weeks)
    unixTime = (lastDate - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    tar = tarfile.open(mode="r:gz", fileobj=uploaded)

    # Find and extract "data.txt" in the archive
    with tar.extractfile(tar.getmember('./data.txt')) as json_file:
        data_text_dict = json.load(json_file)

    # Loop through each member of the tgz file
    for member in tar.getmembers():
        name = member.name
        # Ensure that expected meta files are not computed
        if name[:9] == "./string-" and name[-4:] == ".zip":
            files_found += 1
            try:
                id = int(name[9:-4])  # Removes './string-' prefix and '.zip' from string
                # Check if the id already exists in the database
                if id not in idList:
                    new_files += 1
                    data = json.loads(decompress_zlib(tar.extractfile(member).read()))

                    # -- EDIT DATA TO MAKE UPLOAD PROCESS EASIER --
                    # Make names lowercase
                    data['name'] = data['name'].lower()

                    # Append distance to list if it exists in data.txt
                    face_id = str(data['face_id'])
                    if face_id in data_text_dict['faces']:
                        x = data_text_dict['faces'][face_id]['distance']
                        if x % 100 == 0:
                            data['distance'] = f"{x}m"
                            print(data['distance'])
                        else:
                            yards = round(x * 0.9144)
                            data['distance'] = f"{yards}y"
                    # -- FINISH EDITING DATA --

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
                            issue_code.append(3)
                        stageList.append((data, issue_code))
            except ValueError:
                # In case out of format files were added to archive e.g. "./string-default-string.zip"
                print('invalid filename skipped')

    print("Found {} files in archive".format(files_found))
    print("Found {} new files in archive".format(new_files))
    print("Found {} new relevant files in archive (Made in the last {} weeks)".format(new_files_in_time, weeks))
    print(time.time()-start)

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
