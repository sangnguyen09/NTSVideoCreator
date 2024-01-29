import concurrent.futures
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import as_completed

import gdown
import requests
from tqdm import tqdm


# NUM_PROCESSES = os.cpu_count() # You must experiment with this
NUM_PROCESSES = 4
CHUNK_SIZE = 512 * 1024  # 512KB
MAX_NUMBER_FILES = 50

from colorama import Fore, Style, init

init()

# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"

COLOR_NAME_TO_CODE = {"default": "", "red": Fore.RED, "green": Style.BRIGHT + Fore.GREEN}


def print_text (text, color="default", in_place=False, **kwargs):  # type: (str, str, bool, any) -> None
	"""
	print text to console, a wrapper to built-in print

	:param text: text to print
	:param color: can be one of "red" or "green", or "default"
	:param in_place: whether to erase previous line and print in place
	:param kwargs: other keywords passed to built-in print
	"""
	if in_place:
		print("\r" + ERASE_LINE, end="")
	print(COLOR_NAME_TO_CODE[color] + text + Style.RESET_ALL, **kwargs)


def create_url_github (url):
	"""
	From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
	"""
	repo_only_url = re.compile(r"https:\/\/github\.com\/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}\/[a-zA-Z0-9]+$")
	re_branch = re.compile("/(tree|blob)/(.+?)/")
	
	# Check if the given url is a url to a GitHub repo. If it is, tell the
	# user to use 'git clone' to download it
	if re.match(repo_only_url, url):
		print_text("✘ The given url is a complete repository. Use 'git clone' to download the repository",
			"red", in_place=True)
		sys.exit()
	
	# extract the branch name from the given url (e.g master)
	branch = re_branch.search(url)
	download_dirs = url[branch.end():]
	api_url = (url[:branch.start()].replace("github.com", "api.github.com/repos", 1) +
			   "/contents/" + download_dirs + "?ref=" + branch.group(2))
	return api_url, download_dirs


def download_github (repo_url, flatten=False, output_dir="./"):
	""" Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
	 sub-directories will be pulled upwards into the root folder. """
	
	# generate the url which returns the JSON data
	api_url, download_dirs = create_url_github(repo_url)
	print(api_url)
	# To handle file names.
	if not flatten:
		if len(download_dirs.split(".")) == 0:
			dir_out = os.path.join(output_dir, download_dirs)
		else:
			dir_out = os.path.join(output_dir, "/".join(download_dirs.split("/")[:-1]))
	else:
		dir_out = output_dir
	
	try:
		opener = urllib.request.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib.request.install_opener(opener)
		response = urllib.request.urlretrieve(api_url)
	except KeyboardInterrupt:
		# when CTRL+C is pressed during the execution of this script,
		# bring the cursor to the beginning, erase the current line, and dont make a new line
		print_text("✘ Got interrupted", "red", in_place=True)
		sys.exit()
	
	if not flatten:
		# make a directory with the name which is taken from
		# the actual repo
		os.makedirs(dir_out, exist_ok=True)
	
	# total files count
	total_files = 0
	
	with open(response[0], "r") as f:
		data = json.load(f)
		# getting the total number of files so that we
		# can use it for the output information later
		total_files += len(data)
		
		# If the data is a file, download it as one.
		if isinstance(data, dict) and data["type"] == "file":
			try:
				# download the file
				opener = urllib.request.build_opener()
				opener.addheaders = [('User-agent', 'Mozilla/5.0')]
				urllib.request.install_opener(opener)
				urllib.request.urlretrieve(data["download_url"], os.path.join(dir_out, data["name"]))
				# bring the cursor to the beginning, erase the current line, and dont make a new line
				print_text("Downloaded: " + Fore.WHITE + "{}".format(data["name"]), "green", in_place=True)
				
				return total_files
			except KeyboardInterrupt:
				# when CTRL+C is pressed during the execution of this script,
				# bring the cursor to the beginning, erase the current line, and dont make a new line
				print_text("✘ Got interrupted", 'red', in_place=False)
				sys.exit()
		
		for file in data:
			file_url = file["download_url"]
			file_name = file["name"]
			file_path = file["path"]
			
			if flatten:
				path = os.path.basename(file_path)
			else:
				path = file_path
			dirname = os.path.dirname(path)
			
			if dirname != '':
				os.makedirs(os.path.dirname(path), exist_ok=True)
			else:
				pass
			
			if file_url is not None:
				try:
					opener = urllib.request.build_opener()
					opener.addheaders = [('User-agent', 'Mozilla/5.0')]
					urllib.request.install_opener(opener)
					# download the file
					urllib.request.urlretrieve(file_url, path)
					
					# bring the cursor to the beginning, erase the current line, and dont make a new line
					print_text("Downloaded: " + Fore.WHITE + "{}".format(file_name), "green", in_place=False, end="\n",
						flush=True)
				
				except KeyboardInterrupt:
					# when CTRL+C is pressed during the execution of this script,
					# bring the cursor to the beginning, erase the current line, and dont make a new line
					print_text("✘ Got interrupted", 'red', in_place=False)
					sys.exit()
			else:
				download_github(file["html_url"], flatten, download_dirs)
	
	return total_files


# def main ():
# 	if sys.platform != 'win32':
# 		# disbale CTRL+Z
# 		signal.signal(signal.SIGTSTP, signal.SIG_IGN)
#
# 	parser = argparse.ArgumentParser(description="Download directories/folders from GitHub")
# 	parser.add_argument('urls', nargs="+",
# 		help="List of Github directories to download.")
# 	parser.add_argument('--output_dir', "-d", dest="output_dir", default="./",
# 		help="All directories will be downloaded to the specified directory.")
#
# 	parser.add_argument('--flatten', '-f', action="store_true",
# 		help='Flatten directory structures. Do not create extra directory and download found files to'
# 			 ' output directory. (default to current directory if not specified)')
#
# 	args = parser.parse_args()
#
# 	flatten = args.flatten
# 	# for url in args.urls:
# 	# 	total_files = download(url, flatten, args.output_dir)
# 	#
# 	# print_text("✔ Download complete", "green", in_place=True)


def _download_part (url_and_headers_and_partfile):
	url, headers, partfile = url_and_headers_and_partfile
	response = requests.get(url, headers=headers)
	# setting same as below in the main block, but not necessary:
	chunk_size = 1024 * 1024
	
	# Need size to make tqdm work.
	size = 0
	with open(partfile, 'wb') as f:
		for chunk in response.iter_content(chunk_size):
			if chunk:
				size += f.write(chunk)
	return size


def _make_headers (start, chunk_size):
	end = start + chunk_size - 1
	return {'Range': f'bytes={start}-{end}'}


def dowload_file_thread (url, file_name):
	# url = 'https://download.samplelib.com/mp4/sample-30s.mp4'
	# file_name = 'video.zz'
	response = requests.get(url, stream=True)
	file_size = int(response.headers.get('content-length', 0))
	chunk_size = 1024 * 1024
	
	chunks = range(0, file_size, chunk_size)
	my_iter = [[url, _make_headers(chunk, chunk_size), f'{file_name}.part{i}'] for i, chunk in enumerate(chunks)]
	
	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
		jobs = [executor.submit(_download_part, i) for i in my_iter]
		
		with tqdm(total=file_size, unit='iB', unit_scale=True, unit_divisor=chunk_size, leave=True, colour='cyan') as bar:
			for job in as_completed(jobs):
				size = job.result()
				bar.update(size)
	
	with open(file_name, 'wb') as outfile:
		for i in range(len(chunks)):
			chunk_path = f'{file_name}.part{i}'
			with open(chunk_path, 'rb') as s:
				outfile.write(s.read())
			os.remove(chunk_path)


if __name__ == "__main__":
	# main()
	# start = time.time()
	# # url = "https://drive.google.com/file/d/1ktcQqmqLbDR6Q-MNVvr7bGK5C3TammHa/view?usp=share_link"
	# url, file_name = create_url_github("https://github.com/sangnguyen09/test/blob/main/ffocr.7z")
	# # # print(file_name)
	# # # file_name =
	# # downloader = my_download(url, "debian-11.0.0-amd64-DVD-1.iso")
	# # downloader.run()
	# id = "1ktcQqmqLbDR6Q-MNVvr7bGK5C3TammHa"
	#
	#
	# print(time.time() - start)
	
	# importing shutil module
	import shutil
	
	# cmd
	cmd = 'python'
	
	# Using shutil.which() method
	locate = shutil.which(cmd)
	
	# Print result
	print(locate)
