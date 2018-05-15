# encoding=utf-8
import os
import paramiko
import time
from paramiko import SSHException
import argparse
from getpass import getpass

argparser = argparse.ArgumentParser(description="PJWSTK data searcher.")

argparser.add_argument("mode", choices=['search', 'download'],
                       help='Program purpose.', default='search')

argparser.add_argument("patterns", nargs="*",
                       help="Patterns to search or file path to download.")

argparser.add_argument("username", help="University login.", type=str)

argparser.add_argument("--index_list", type=str, help="Path to file"
                       "with students' index numbers", default=os.path.join(
                           os.getcwd(), "indexes.txt"))

argparser.add_argument("-t", "--timeout", type=int, help="Timeout between "
                                                         "each ssh command",
                       default=2)

argparser.add_argument("-k", "--key", type=str,
                       help="Path to private ssh key file.")

argparser.add_argument("-o", "--output", type=str, help="Path to output file, "
                       "only in download mode.",  default=os.path.join(
                           os.getcwd(), "output.txt"))

argparser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose mode.")

settings = argparser.parse_args()

if settings.key:
    rsakey = paramiko.RSAKey.from_private_key_file(settings.key)
result_list = []
index_list = []

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

with open(str(settings.index_list), 'r') as f:
	index_list = [line.replace("\n", "") for line in f]
	for index in index_list:
		if index[0] is not 's':
			index = 's' + index
	print("Data prepared, attempting to establish a secure connection.")

try:
	if settings.key:
		client.connect("szuflandia.pjwstk.edu.pl", username=settings.username,
                       pkey=rsakey or None)
	else:
		client.connect("szuflandia.pjwstk.edu.pl", username=settings.username,
                        password=getpass(prompt="Password: "))
except SSHException as e:
	print("Connection failed, error:\n {}".format(e))
else:
	print("Connection successfull, let's roll.")


for pattern in settings.patterns:
	print("Searching for {} pattern.".format(pattern))
	for index in index_list[:20]:
		print("Mining data from {} student.".format(index))
		try:
			stdin, stdout, stderr = client.exec_command(
				"find /home/PJWSTK/{} -type f -name \"{}\"".format(index,
				                                                   pattern))
			time.sleep(settings.timeout)
		except SSHException as e:
			print("An error ocurred when trying to mine data: {}".format(e))
		stdout._set_mode('b')
		for line in stdout.readlines():
			result_list.append(line)

with open(settings.output, "ab") as f:
    for line in result_list:
        f.write(line)

#with open(settings.output, "r") as f:
#    fdata = f.read()
#    fdata.replace("deadbeef", "\n")

#with open(settings.output, "w") as f:
#    f.write(fdata)
