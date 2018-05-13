# encoding=utf-8
import os
import paramiko
import time
from paramiko import SSHException
import argparse

argument_parser = argparse.ArgumentParser(description="PJWSTK data searcher.")
argument_parser.add_argument("-d", "--download", action="append", nargs=1)
argument_parser.add_argument("-s", "--search", action="append", nargs="*")
argument_parser.add_argument("-o", "--output", nargs=1)
argument_parser.add_argument("")

key_path = "C:/Users/Paweł/.ssh/id_rsa"
index_file = "C:/Users/Paweł/Documents/workspace/indeksy.txt"
key = paramiko.RSAKey.from_private_key_file(key_path)
result_List = []
index_list = []

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


with open(index_file, 'r') as f:
    index_list = [line.replace("\n", "") for line in f]
    print("Data prepared, attempting to establish a secure connection.")
    try:
        client.connect("szuflandia.pjwstk.edu.pl", username="s13705", pkey=key)
    except SSHException as e:
        print("Connection failed, error:\n {}".format(e))
    else:
        print("Connection successfull, let's roll.")
    try:
        for index in index_list:
            print("Mining data from {} student.".format(index))
            stdin, stdout, stderr = client.exec_command("find /home/PJWSTK/{} -type f -name \"{}\"".format(index, "TIN"))
            stdin.close()
            stdout._set_mode('b')
            time.sleep(2)
            for line in stdout.readlines():
                result_List.append(line)
    except:
        print("An Error ocurred, closing secure connection!")
    finally:
        print("Searching finished, closing secure connection.")
        client.close()

os.chdir("C:/Users/Paweł/Documents/workspace")
with open("results.txt", "ab") as f:
    for line in result_List:
        f.write(line)
        f.write(bytes("deadbeef", encoding='utf-8'))

fdata = None
with open("results.txt", "r") as f:
    fdata = f.read()

fdata.replace("deadbeef", "\n")

with open("results.txt", "w") as f:
    f.write(fdata)
