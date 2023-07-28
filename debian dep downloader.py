import os
import re
import shutil
import requests
from urllib.parse import unquote

CWD = os.getcwd()
WEBSITE = r"https://deb.debian.org"

if __name__ == "__main__":
    
    #find pcapng file in current directory
    for file_name in os.listdir(CWD):
        if file_name.endswith(".txt"):
            print(file_name)
            break

    mroot_folder = os.path.join(CWD, r"rpi\var\www\deb")
    if not os.path.exists(mroot_folder):
        os.mkdir(mroot_folder)

    with open(os.path.join(CWD, file_name), 'r') as fp:
        # read all lines and put valid lines in a list
        valid_lines = [line for line in fp.readlines() if re.search(r"GET", line) and re.search(r"HTTP", line)]

    for line in valid_lines:
        if "preseed.cfg" in  line:
            continue
        
        multi_request_check = re.findall("GET [^ ]* HTTP", line)
        if len(multi_request_check) > 1:
            valid_lines += multi_request_check
            continue
        else:
            line = multi_request_check[0]
            # print(line)

        start_idx = re.search(f"/[A-Za-z]", line)
        tmp = line[start_idx.start():]
        end_idx = re.search("\s", tmp)
        path = tmp[:end_idx.start()]
        file_dir = path[:path.rfind(r"/")]

        percent_decoded_path = unquote(path)
        # print(file_dir)
        # print(percent_decoded_path)
        print(path)
        print()
        file_dir = file_dir.replace("/", "\\")
        file_dir = f"{mroot_folder}{file_dir}"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with requests.get(f"{WEBSITE}{path}", stream=True) as r:
            with open(f"{mroot_folder}\{percent_decoded_path}", 'wb') as f:
                shutil.copyfileobj(r.raw, f)
