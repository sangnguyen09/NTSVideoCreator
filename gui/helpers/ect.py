import base64
import hashlib
import json
import os
import platform
import random
import shutil
import struct
import time

import psutil  # pip install psutil
import wmi  # pip install wmi pywin32
from AesEverywhere import aes256  # pip install aes-everywhere
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

from gui.helpers.constants import PAE_LG


#

# def mh_ae (data_json: dict, p_k=PAE_LG):
# 	return aes256.encrypt(json.dumps(data_json), p_k).decode('utf-8')
#
#
# def gm_ae (code: str, p_k=PAE_LG):
# 	return json.loads((aes256.decrypt(code, p_k)))
#

def _ge_k_t ():
	length = 6
	timee = time.time().__str__()
	print(str(int(float(timee))).encode())
	buffer = bytearray(length)
	first_byte = b''
	struct.pack_into('>i', buffer, 0, int(float(timee)))
	for i in range(length):
		# if i > 5:
		value = struct.unpack_from('B', buffer, i)[0]
		first_byte += chr(value).encode('latin-1')
	print(first_byte.decode('latin-1'))
	return first_byte


# except:
# 	print("Bạn là Cracker")


def mh_ae (raw, p_k=PAE_LG):
	try:
		length = 32
		data = json.dumps(raw)
		# __key__ = k if k is not None else _ge_k(data)
		__key__ = random.randbytes(length)
		
		# print(__key__)
		BS = AES.block_size
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		
		data = base64.b64encode(pad(data).encode('utf8'))
		
		ivt = get_random_bytes(AES.block_size)
		iv = ivt[0:6] + random.randbytes(8) + ivt[6:]
		cipher = AES.new(key=__key__, mode=AES.MODE_CFB, iv=ivt)
		data_en = cipher.encrypt(data)
		data = iv + data_en[:2] + random.randbytes(36) + data_en[2:]
		
		return base64.b64encode(data[:19] + __key__ + data[19:]).decode()
	except:
		pass


def gm_ae (data, p_k=PAE_LG):
	try:
		length = 32
		unpad = lambda s: s[:-ord(s[-1:])]
		enc = base64.b64decode(data)
		# print(enc.decode('latin-1'))
		__key__, contt = enc[19:length + 19], enc[:19] + enc[length + 19:]
		iv = contt[0:6] + contt[14:AES.block_size + 8]
		da_e = contt[AES.block_size + 8:]
		da_e = da_e[0:2] + da_e[38:]
		cipher = AES.new(__key__, AES.MODE_CFB, iv)
		return json.loads(unpad(base64.b64decode(cipher.decrypt(da_e)).decode('utf8')))
	except:
		pass
def mh_ae_w (raw, p_k=PAE_LG):
	try:
		length = 16
		data = json.dumps(raw)
		# __key__ = k if k is not None else _ge_k(data)
		key = random.randbytes(length)
		
		# print(__key__)
		BS = AES.block_size
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		
		data = base64.b64encode(pad(data).encode('utf8'))
		
		ivt = get_random_bytes(AES.block_size)
		iv = ivt[0:4] + random.randbytes(16) + ivt[4:]
		cipher = AES.new(key=key, mode=AES.MODE_CFB, iv=ivt)
		data_en = cipher.encrypt(data)
		data = iv + data_en[:6] + random.randbytes(48) + data_en[6:]
		
		return base64.b64encode(data[:16] + key + data[16:]).decode()
	except:
		pass


# print("Bạn là Cracker")


def gm_ae_w (data, p_k=PAE_LG):
	try:
		length = 16
		unpad = lambda s: s[:-ord(s[-1:])]
		enc = base64.b64decode(data)
		# print(enc.decode('latin-1'))
		key, contt = enc[16:length + 16], enc[:16] + enc[length + 16:]
		iv = contt[0:4] + contt[20:AES.block_size + 16]
		da_e = contt[AES.block_size + 16:]
		da_e = da_e[0:6] + da_e[54:]
		cipher = AES.new(key, AES.MODE_CFB, iv)
		return json.loads(unpad(base64.b64decode(cipher.decrypt(da_e)).decode('utf8')))
	except:
		pass



# print("Bạn là Cracker")


def cr_pc (tool_code="autosub"):
	try:
		c = wmi.WMI()
		# dic = {}
		# for item in c.Win32_PhysicalMedia():
		#     # print(item)
		#     dic[str(item.wmi_property('Tag').value).replace('\\','')] = str(item.wmi_property('SerialNumber').value).replace(' ','')
		# print(dic)
		# diskserial = dic['.PHYSICALDRIVE0']
		
		diskserial = c.Win32_PhysicalMedia()[0].wmi_property('SerialNumber').value.strip()  # 0 thuowngf la o C
	
	except:
		diskserial = ''
	try:
		computername = str(platform.node())
	except:
		computername = ''
	
	try:
		hdtotal, hdused, hdfree = shutil.disk_usage(os.getenv('SystemDrive'))
	# print(hdtotal, hdused, hdfree)
	except:
		hdtotal = ''
	
	try:
		ramsize = str(psutil.virtual_memory().total)
	except:
		ramsize = ''
	
	try:
		ncpu = str(psutil.cpu_count(logical=True))
	except:
		ncpu = ''
	
	key_reg = computername + ' ' + diskserial + ' ' + str(hdtotal) + ' ' + ramsize + ' ' + ncpu + ' '
	# print(key_reg)
	key_reg = hashlib.md5(key_reg.encode('utf-8')).hexdigest()
	# print(key_reg)
	if tool_code =='autosub':
		return mh_ae(key_reg)
	else:
		return mh_ae_w(key_reg)


if __name__ == '__main__':  # U2FsdGV
	# tess = ""
	
	# base64_dict = base64.b64encode(string) ZmZtcGVnIC1pICJFOlxQcm9 YW5oZHNkLm1rdiI
	# sample_string_bytes = string.encode("ascii")

	pass
