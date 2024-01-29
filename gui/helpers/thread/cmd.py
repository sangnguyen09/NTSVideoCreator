import subprocess
import tempfile
import time
import zipfile

CREATE_NO_WINDOW = 0x08000000


def run_cmd (command: str):
	subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)


def run_cmd_result (command: str):
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
		creationflags=CREATE_NO_WINDOW)
	return proc.communicate()[0].decode('ascii').split('\r\n')


if __name__ == '__main__':
	start = time.time()
	path = "E:/Project/Python/TachSubVideo/videocr-PaddleOCR/dist/ffocr.zip"
	dir_extract = "E:/Project/Python/TachSubVideo/videocr-PaddleOCR/New folder/"
	dir_extract = tempfile.TemporaryDirectory()
	command = 'E:/Project/Python/ReviewPhim/7z x "E:/Project/Python/TachSubVideo/videocr-PaddleOCR/dist/ffocr.7z" -y -o"E:/Project/Python/TachSubVideo/videocr-PaddleOCR/New folder/"'
	# process = subprocess.Popen(
	# 	command,
	# 	stdout=subprocess.PIPE,
	# 	stderr=subprocess.STDOUT,
	# 	shell=True,
	# 	# creationflags=0x08000000,
	# 	encoding='utf-8',
	# 	errors='replace'
	# )
	# while True:
	# 	realtime_output = process.stdout.readline()
	# 	if realtime_output == '' and process.poll() is not None:
	# 		break
	# 	if realtime_output:
	# 		print(realtime_output.strip())
	
	opener, mode = zipfile.ZipFile, "r"
	
	with opener(path, mode) as f:
		f.extractall(path=dir_extract)
	
	# kêt thúc code
	end = time.time()
	# and end time in milli. secs
	print("Thời gian thực thi là :",
		(end - start) * 10 ** 3, "ms")
	print("Thời gian thực thi là :",
		((end - start) * 10 ** 3) / 1000, "s")
