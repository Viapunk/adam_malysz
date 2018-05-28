# encoding=utf-8
import os
import re

import paramiko
import time
from paramiko import SSHException
import argparse
from getpass import getpass


class adam_malysz(object):
	result_list = set()
	index_list = []
	settings = None
	rsakey = None
	client = None

	def make_connection(self):
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			if self.settings.key:
				self.client.connect("szuflandia.pjwstk.edu.pl",
														username=self.settings.username,
														pkey=self.rsakey or None)
			else:
				self.client.connect("szuflandia.pjwstk.edu.pl",
														username=self.settings.username, password=getpass(
						prompt="Password: "))
		except SSHException as e:
			print("Connection failed, error:\n {}".format(e))
			return -1
		else:
			print("Connection successfull, let's roll.")
			return 0;

	def close_connection(self):
		""" Closes SSH connection. """
		self.client.close()

	def parse_arguments(self):
		""" Initializes and parses arguments in an easy to use way. """
		argparser = argparse.ArgumentParser(
			description="PJWSTK data searcher.")

		argparser.add_argument("mode", choices=['search', 'download'],
													 help='Program purpose.', default='search')

		argparser.add_argument("patterns", nargs="*", help="Patterns to search "
																											 "or file path to download.")

		argparser.add_argument("username", help="University login.", type=str)

		argparser.add_argument("--index_list", type=str, help="Path to file"
																													"with students' index numbers")

		argparser.add_argument("-t", "--timeout", type=int,
													 help="Timeout between each ssh command",
													 default=0.5)

		argparser.add_argument("-k", "--key", type=str,
													 help="Path to private ssh key file.")

		argparser.add_argument("-o", "--output", type=str, help="Path to output "
																														"file, only in download mode.",
													 default=os.path.join(os.getcwd(), "output.txt"))

		argparser.add_argument("-v", "--verbose", action="store_true",
													 help="Verbose mode.")

		self.settings = argparser.parse_args()

		if self.settings.key:
			self.rsakey = paramiko.RSAKey.from_private_key_file(
				self.settings.key)

	def write_data_to_file(self):
		""" Writes result data to a file."""
		with open(self.settings.output, "ab") as f:
			for line in self.result_list:
				f.write(line)

		with open(self.settings.output, "r") as f:
			fdata = f.read()
			fdata.replace("deadbeef", "\n")

		with open(self.settings.output, "w") as f:
			f.write(fdata)

	def prepare_data(self):
		""" Prepares data to be used by SSH client. If index_file is not
				specified, It will generate list with all available indexes with
				proper permissions.
		"""
		if self.settings.index_list is None:
			self.make_connection()
			result = self.execute_remote_command("ls -la /home/PJWSTK/")
			for line in result[3:]:
				if len(re.findall("(rwx)|(r-x)$", line.split()[0])):
					self.index_list.append(line.split()[8])

		else:
			with open(str(self.settings.index_list), 'r') as f:
				self.index_list = [line.replace("\n", "") for line in f]
				for index in self.index_list:
					if index[0] is not 's':
						index = 's' + index
		print("Data prepared")

	def krec_malysza(self, patterns=None):
		"""
		Searches for files containing specific pattern.
		Gets:
		- pattern - [str] Text pattern to search in each index.
		"""
		if patterns is None:
			patterns = self.settings.patterns
		find_command = "find /home/PJWSTK/{} -type f -name \"{}\""
		for pattern in patterns:
			print("Searching for {} pattern.".format(pattern))
			for index in self.index_list:
				print("Mining data from {} student.".format(index))
				try:
					result = self.execute_remote_command(find_command.format(index,
																																	 pattern))
					time.sleep(self.settings.timeout)
				except SSHException as e:
					print(
						"An error ocurred when trying to mine data: {}"
							.format(e))
				self.result_list = set(line for line in result)

	def execute_remote_command(self, command, silent=False):
		"""
		Executes command on through SSH client.
		Gets:
		- command - [str] Command to be executed remotely
		- silent - [bool] True if function shouldn't return anything, otherwise
			False

		Returns:
		- [list<str>] List containing lines returned by executed command
		"""
		stdin, stdout, stderr = self.client.exec_command(command)
		#stdout._set_mode('b')
		if not silent:
			return stdout.readlines()




if __name__ == "__main__":
	skoczek = adam_malysz()
	skoczek.parse_arguments()
	skoczek.prepare_data()
	skoczek.make_connection()
	skoczek.krec_malysza()
	skoczek.close_connection()