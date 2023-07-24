# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 17:39:59 2023

@author: Wei qiang
"""

import os, imageio, json, argparse
from md5hash import scan

from PIL import Image, ImageSequence
import numpy as np

from scipy.io import wavfile

class tools:
	def __init__(self):
		return

	def transDeci2Quater(self, deci_num: int, num_len: int = None) -> str:
		remainder_list = []

		while True:
			quot = deci_num//4
			remainder = deci_num%4
			remainder_list.append(str(remainder))

			if quot == 0:
				break
			else:
				deci_num = quot

		quater_num = "".join(remainder_list[::-1])

		if num_len != None:
			if len(remainder_list) > num_len:
				raise numberLengthSetError
				print("The length of quaternary number is longer than you set, please check it out. ")

			quater_num = "0"*(num_len - len(quater_num)) + quater_num

		return quater_num

	def transDeciList2QuterStr(self, deci_list: list) -> str:
		max_num = max(deci_list)
		set_num_len = len(self.transDeci2Quater(max_num))
		quater_str = ""

		for deci_num in deci_list:
			quater_num = self.transDeci2Quater(deci_num, num_len = set_num_len)
			quater_str += quater_num

		return quater_str, set_num_len

	def extractImage(self, input_path: str, output_path: str) -> int:
		'''
		from GIF
		'''

		with Image.open(input_path) as im:
			index = 0
			for frame in ImageSequence.Iterator(im):
				_out_path = "{}_{}.bmp".format(output_path, index)
				frame.save(_out_path)
				index += 1

		return index

	def produceGIF(self, image_dir: str, output_path: str, duration: float = 1):

		iamge_path_list = [image_dir+os.sep+i for i in os.listdir(image_dir) if i.endswith("bmp")]
		frames = []
		for image_path in iamge_path_list:
			frames.append(imageio.v2.imread(image_path))

		imageio.mimsave(output_path, frames, "GIF", duration = duration)

	def extendMappingRegulation(self) -> dict:

		# repeat_replace_dic = {"AAAA":"ATGCA","TTTT":"ATGCT","CCCC":"ATGCG","GGGG":"ATGCC"}
		repeat_replace_dic = {"CCCC":"ATGCC","GGGG":"ATGCG","TTTT":"ATGCT","AAAA":"ATGCA"}
		nt_dic = {"0":"A", "1":"T", "2":"C", "3":"G"}

		# get select units, len = 6
		select_unit_list = []
		for i in range(4096):
			unit_num = self.transDeci2Quater(i, 6)
			unit_seq = "".join([nt_dic[i] for i in unit_num])

			gc = unit_seq.count("G")+unit_seq.count("C")
			if gc != 3:
				continue


			judge_list = [unit_seq[:4]=="ATGC", unit_seq[1:5]=="ATGC", unit_seq[2:]=="ATGC", unit_seq[3:]=="ATG", 
						unit_seq[4:]=="AT", unit_seq[:3]=="TGC", unit_seq[:3]=="AAA", unit_seq[:3]=="TTT", 
						unit_seq[:3]=="CCC", unit_seq[:3]=="GGG", unit_seq[3:]=="AAA", unit_seq[3:]=="TTT", 
						unit_seq[3:]=="GGG", unit_seq[3:]=="CCC"]

			if True in judge_list:
				continue

			select_unit_list.append(unit_seq)

		# mapping regulation, for 5 -> 6
		mapping_dic = {}
		for i in range(1024):
			unit_num = self.transDeci2Quater(i, 5)
			unit_seq = "".join([nt_dic[i] for i in unit_num])
			mapping_dic[unit_seq] = select_unit_list[i]

		return mapping_dic, repeat_replace_dic

	def extendSequence(self, nt_seq: str) -> str:

		mapping_dic, repeat_replace_dic = self.extendMappingRegulation()

		# extend sequence 5-> 6
		i = 0
		extend_seq = ""
		while True:
			ori_unit = nt_seq[i:i+5]

			if len(ori_unit) < 5:
				extend_seq += ori_unit
				break
			extend_seq += mapping_dic[ori_unit]
			i += 5

		# print(extend_seq)
		# replace repeat
		for ori_unit, new_unit in repeat_replace_dic.items():
			extend_seq = extend_seq.replace(ori_unit, new_unit)

		# print(extend_seq)
		return extend_seq

	def getOrinalSeq(self, nt_seq: str) -> str:
		encode_mapping_dic, encode_repeat_replace_dic = self.extendMappingRegulation()

		mapping_dic = {value: key for key, value in encode_mapping_dic.items()}
		# repeat_replace_dic = {value: key for key, value in encode_repeat_replace_dic.items()}

		# recover repeat
		key_list = list(encode_repeat_replace_dic.keys())[::-1]
		for key in key_list:
			value = encode_repeat_replace_dic[key]
			nt_seq = nt_seq.replace(value, key)

		# sequence 6 -> 5
		i = 0
		ori_seq = ""
		while True:
			unit = nt_seq[i: i+6]

			if len(unit) < 6:
				ori_seq += unit
				break
			ori_seq += mapping_dic[unit]
			i += 6

		return ori_seq


class lzwEncode:
	def __init__(self, input_path:str, output_path: str):
		self.input_path = input_path
		self.output_path = output_path
		self.input_info = ""
		self.map_dic = {}
		self.lzw_list = []
		self.map_list = []
		self.last_num = 0
		self.quaternary_str = ""
		self.nt_seq = ""
		self.unit_len = 0
		# self.config_dic = {}


	def readFileAndSetDic(self):
		'''
		Placeholder function
		'''
		return 0

	def saveBaseDic(self):
		return 0


	def findLongestUnit(self, init_index: int) -> int:
		'''
		Gets the longest unit that can be matched in the dictionary
		return: unit_len
		'''

		length = 1
		while True:
			_unit = self.input_info[init_index: init_index + length]
			# if init_index+length == len(self.input_info):
			# 	return length

			length += 1
			if _unit in self.map_dic:
				continue	
			else:
				# print(length-2, init_index)
				return length-2

	def lzwEncode(self): 
		'''
		Get the compressed sequence
		'''

		self.input_info += "$"

		i = 0
		while True:
			if i == len(self.input_info)-1:
				break


			if i > 0:
				_key = self.map_list[-1] + self.input_info[i]
				if _key not in self.map_dic:
					self.last_num = len(self.map_dic)
					self.map_dic[_key] = self.last_num
					# print(self.map_dic)

				# print("key", _key)
			unit_len = self.findLongestUnit(i)
			# print("unit_len", unit_len)
			unit = self.input_info[i: i+unit_len]
			self.map_list.append(unit)
			self.lzw_list.append(self.map_dic[unit])

			i += unit_len
			# print(i, len(self.input_info))
			# if i == len(self.input_info):
			# 	break


	def printMessage(self):
		file_size = os.stat(self.input_path).st_size*8
		info_density = file_size/len(self.nt_seq)
		print("File path:\t{}".format(self.input_path))
		print("File size:\t{} bits".format(file_size))
		print("Information density:\t{} bits/nt".format(round(info_density, 2)))
		print("Length of sequence:\t{} nt".format(len(self.nt_seq)))
		print("\n\n")

	def saveResult(self):
		with open(self.output_path, "w") as f:
			f.write(self.nt_seq)

	def main(self):
		nt_dic = {"0":"A", "1":"T", "2":"C", "3":"G"}
		self.readFileAndSetDic()
		self.lzwEncode()
		self.quaternary_str, self.unit_len = tools().transDeciList2QuterStr(self.lzw_list)
		self.nt_seq = "".join([nt_dic[i] for i in self.quaternary_str])
		self.nt_seq = tools().extendSequence(self.nt_seq)
		self.printMessage()
		self.saveResult()
		self.saveBaseDic()


class textWordEncode(lzwEncode):
		
	def readFileAndSetDic(self):
		with open(self.input_path, encoding = "utf-8") as f:
			words = f.read()

		words_list = list(words)

		map_key_list = list(set(words_list))
		map_key_list.sort()

		self.input_info = words
		self.last_num = len(map_key_list)
		self.map_dic = {key: index for index, key in enumerate(map_key_list)}


	def saveBaseDic(self):
		config_dic = {"fileType": "text", "unitLen": self.unit_len, "md5": scan(self.input_path)}

		base_map_dic = {key:value for key, value in self.map_dic.items() if len(key) == 1}
		config_dic["baseMapDic"] = base_map_dic

		json_str = json.dumps(config_dic, indent = 4)
		dic_path = self.output_path +".json"
		with open(dic_path, "w", encoding="utf-8") as f:
			f.write(json_str)


class imageEncode(lzwEncode):
	## new self: [self.wdith, self.height]

	def readFileAndSetDic(self):
		im = Image.open(self.input_path)
		im_array = np.array(im)
		self.height = len(im_array)
		self.wdith = len(im_array[0])

		for line in im_array:
			for r,g,b in line:
				r,g,b = str(r), str(g), str(b)
				r,g,b = ["0"*(3-len(i))+i for i in [r,g,b]]
				self.input_info += r+g+b

		self.map_dic = {str(i): i for i in range(10)}
		self.last_num = len(self.map_dic)
		self._config_dic = {"fileType": "colorImage"}


	def saveBaseDic(self):
		config_dic ={"fileType": self._config_dic["fileType"], "unitLen": self.unit_len, "width": self.wdith, 
					"height": self.height, "md5": scan(self.input_path)}

		json_str = json.dumps(config_dic, indent = 4)
		dic_path = self.output_path +".json"
		with open(dic_path, "w") as f:
			f.write(json_str)


class imageEncodeBW(imageEncode):

	def readFileAndSetDic(self):

		image_raw = Image.open(self.input_path)
		image_black_white = image_raw.convert('1')
		image_black_white.save(self.input_path)

		im = Image.open(self.input_path)
		im_array = np.array(im)
		self.height = len(im_array)
		self.wdith = len(im_array[0])
		for line in im_array:
			# for r,g,b in line:
			for r in line:
				if r == 0:
					self.input_info += "0"
				else:
					self.input_info += "1"
			# self.input_info += "\n"

		self.map_dic = {str(i): i for i in range(2)}
		# self.map_dic["\n"] = 2
		self.last_num = len(self.map_dic)

		self._config_dic = {"fileType": "BlackWhiteImage"}

class gifEncode(imageEncode):

	def main(self):
		image_number = tools().extractImage(self.input_path, self.output_path)

		for i in range(image_number):
			_input_path = "{}_{}.bmp".format(self.output_path, i)
			self.readFileAndSetDic()

		self.lzwEncode()
		self.quaternary_str, self.unit_len = tools().transDeciList2QuterStr(self.lzw_list)
		self.printMessage()


class gifEncodeBW(imageEncodeBW):

	def main(self):
		image_number = tools().extractImage(self.input_path, self.output_path)

		for i in range(image_number):
			_input_path = "{}_{}.bmp".format(self.output_path, i)
			self.readFileAndSetDic()

		self.lzwEncode()
		self.quaternary_str, self.unit_len = tools().transDeciList2QuterStr(self.lzw_list)
		self.printMessage()

class audioEncode(lzwEncode):

	def readFileAndSetDic(self):
		#  new self [self.rate, self.channel, self.min_num, self.sample_len]

		self.rate, wav = wavfile.read(self.input_path)
		self.channel = len(wav[0])

		num_list = []
		for unit in wav:
			num_list += list(unit)
		self.min_num = min(num_list)
		num_list = [i - self.min_num for i in num_list]
		self.sample_len = len(str(max(num_list)))

		for num in num_list:
			self.input_info += "0"*(self.sample_len-len(str(num))) + str(num)

		self.map_dic = {str(i): i for i in range(10)}
		self.last_num = len(self.map_dic)
		self._config_dic = {"fileType": "audio"}

	def saveBaseDic(self):
		config_dic ={"fileType": self._config_dic["fileType"], "unitLen": self.unit_len, "rate": self.rate, 
					"channel": self.channel, "minNum":int(self.min_num), "sampleLen": self.sample_len, 
					"md5": scan(self.input_path)}

		json_str = json.dumps(config_dic, indent = 4)
		dic_path = self.output_path +".json"
		with open(dic_path, "w") as f:
			f.write(json_str)



class lzwDecode:
	def __init__(self, nt_seq_path:str = "", save_path: str = ""):
		self.nt_seq_path = nt_seq_path
		self.save_path = save_path
		self.lzw_list = []
		self.info_str = ""
		self.config_dic = {}
		self.nt_seq = ""
		self.quaternary_str = ""
		self.map_dic = {}

	def readFile(self):
		with open(self.nt_seq_path) as f:
			self.nt_seq = f.read().strip()

	def getQuateryStr(self):
		nt_dic = {"A":"0", "T":"1", "C":"2", "G":"3"}
		self.quaternary_str = "".join([nt_dic[i] for i in self.nt_seq])

	def getConfigDic(self):
		config_dic_path = self.nt_seq_path + ".json"
		with open(config_dic_path) as f:
			json_str = f.read()

		self.config_dic = json.loads(json_str)


	def setConfig(self):
		return 0

	def lzwDecode(self):
		i = 0
		while True:
			try:
				lzw_num = int(self.quaternary_str[i*self.unit_len: (i+1)*self.unit_len], 4)
			except ValueError:
				break
			self.lzw_list.append(lzw_num)
			i += 1

			if i == 1:
				continue

			map_unit = self.map_dic[self.lzw_list[-2]]
			self.info_str += map_unit
			if lzw_num in self.map_dic:
				self.map_dic[len(self.map_dic)] = map_unit + self.map_dic[lzw_num][0]
			else:
				if lzw_num == len(self.map_dic):
					self.map_dic[len(self.map_dic)] = map_unit + map_unit[0]

		self.info_str += self.map_dic[lzw_num]



	def saveFile(self):
		return 0

	def printMessage(self):
		print("File type: ", self.config_dic["fileType"])
		print("MD5 of original file is: ", self.config_dic["md5"])
		print("MD5 of decoding file is: ", scan(self.save_path))

	def main(self):
		self.readFile()
		self.nt_seq = tools().getOrinalSeq(self.nt_seq)
		self.getQuateryStr()
		self.getConfigDic()
		self.setConfig()
		self.lzwDecode()
		self.saveFile()
		self.printMessage()


class textWordDecode(lzwDecode):
	def setConfig(self):
		map_dic = self.config_dic["baseMapDic"]
		self.map_dic = {value:key for key, value in map_dic.items()}
		self.unit_len = self.config_dic["unitLen"]

	def saveFile(self):
		self.save_path += ".txt"

		with open(self.save_path, "w", encoding="utf-8") as f:
			f.write(self.info_str)


class imageDecode(lzwDecode):

	def setConfig(self):
		self.map_dic = {i: str(i) for i in range(10)}
		self.unit_len = self.config_dic["unitLen"]
		self.width, self.height = self.config_dic["width"], self.config_dic["height"]

	def saveFile(self):
		self.save_path += ".bmp"
		im = Image.new("RGB", (self.width, self.height))
		pix = im.load()

		i = 0
		for x in range(self.height):
			for y in range(self.width):
				pix[y,x] = (int(self.info_str[i:i+3]), int(self.info_str[i+3:i+6]), int(self.info_str[i+6:i+9]))
				i += 9

		im.save(self.save_path,"BMP")

	def printMessage(self):
		print("File type: ", self.config_dic["fileType"])
		print("MD5 of original file is: ", self.config_dic["md5"])
		print("MD5 of decoding file is: {}\nThe MD5 code may be different with original image file, but don't worry!".format( 
			scan(self.save_path)))

class imageDecodeBW(imageDecode):
	# reset map_dic
	def setConfig(self):
		self.map_dic = {i: str(i) for i in range(2)}
		self.unit_len = self.config_dic["unitLen"]
		self.width, self.height = self.config_dic["width"], self.config_dic["height"]

	def saveFile(self):
		self.save_path += ".bmp"
		im = Image.new("1", (self.width, self.height))
		pix = im.load()

		i = 0
		for x in range(self.height):
			for y in range(self.width):
				_num = int(self.info_str[i])
				pix[y,x] = _num
				# if _num == 0:
				# 	pix[y,x] = (0,0,0)
				# else:
				# 	pix[y,x] = (255,255,255)
				i += 1

		im.save(self.save_path, "BMP")


class audioDecode(lzwDecode):
	def setConfig(self):
		self.map_dic = {i: str(i) for i in range(10)}
		self.unit_len = self.config_dic["unitLen"]

		self.rate, self.channel = self.config_dic["rate"], self.config_dic["channel"], 
		self.min_num, self.sample_len = self.config_dic["minNum"], self.config_dic["sampleLen"]

	def saveFile(self):
		self.save_path += ".wav"

		_i = 0
		num_list = []
		for i in range(0, len(self.info_str), self.sample_len):
			_num = int(self.info_str[i: i+self.sample_len]) + self.min_num

			if self.channel == 1:
				num_list.append([_num])
			else:
				if _i%2 == 0:
					_num_list = [_num]
				else:
					_num_list.append(_num)
					num_list.append(_num_list)
				_i += 1

		num_array = np.array(num_list, dtype = np.int16)
		wavfile.write(self.save_path, self.rate, num_array)


def encodeMain(input_path, output_path):
	'''
	The file suffix of black white images should be "bw.bmp", which sperates from color images.
	image_type in ["color", "blackWhite"]
	'''

	if input_path.endswith("txt"):
		cl = textWordEncode(input_path, output_path)

	elif input_path.endswith("bw.bmp"):
		cl = imageEncodeBW(input_path, output_path)

	elif input_path.endswith("bmp"):
		cl = imageEncode(input_path, output_path)

	elif input_path.endswith("wav"):
		cl = audioEncode(input_path, output_path)

	cl.main()

	return cl


def decodeMain(input_path, output_path):
	_cl = lzwDecode(input_path, output_path)
	_cl.getConfigDic()
	_dic = _cl.config_dic
	file_type = _dic["fileType"]

	if file_type == "text":
		cl = textWordDecode(input_path, output_path)

	elif file_type == "colorImage":
		cl = imageDecode(input_path, output_path)

	elif file_type == "BlackWhiteImage":
		cl = imageDecodeBW(input_path, output_path)

	elif file_type == "audio":
		cl = audioDecode(input_path, output_path)

	cl.main()

	return cl


if __name__ == "__main__":

	def liuxCommand():
		parser = argparse.ArgumentParser()
		parser.add_argument("i", help = "Input path.")
		parser.add_argument("o", help = "Save path. If [m]==[Encode], ending with 'seq'")
		parser.add_argument("-m","--mode", help = "[Encode] or [Decode]")
		args = parser.parse_args()

		return args.i, args.o, args.mode

	input_path, output_path, mode = liuxCommand()
	if mode == "Encode":
		cl_e = encodeMain(input_path, output_path)
	else:
		cl_d = decodeMain(input_path, output_path)



	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/input/lunyu_xueer.txt"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/lunyu_xueer.txt.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/input/test.txt"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/test.txt.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/input/7.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/7.bmp.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/input/8.bw.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/8.bw.bmp.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/input/suansuan_sssmall.wav"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/suansuan_sssmall.wav.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/lzw.txt"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/lzw.txt.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/lunyu_xueer.txt"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/lunyu_xueer.txt.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/smile.bw.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/smile.bw.bmp.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/smile.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/smile.bmp.seq"


	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/upset.bw.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/upset.bw.bmp.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/earth.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/earth.bmp.seq"

	# input_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/input/panda.bw.bmp"
	# output_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/panda.bw.bmp.seq"



	# cl_e = encodeMain(input_path, output_path)
	# info = cl_e.input_info
	# lzw_list = cl_e.lzw_list
	# map_dic = cl_e.map_dic
	# quater_str = cl.quaternary_str
	# unit_len = cl.unit_len

	######################################## DECODE ####################################
	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/lunyu_xueer.txt.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/lunyu_xueer.txt.seq.decode"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/lzw.txt.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/lzw.txt.seq.decode"


	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/7.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/7.bmp.seq.decode"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/8.bw.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/8.bw.bmp.seq.decode"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/suansuan_sssmall.wav.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/2-test/output/suansuan_sssmall.wav.seq.decode"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/lzw.txt.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/lzw.txt.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/lunyu_xueer.txt.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/lunyu_xueer.txt.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/smile.bw.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/smile.bw.bmp.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/smile.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/smile.bmp.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/upset.bw.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/upset.bw.bmp.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/earth.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/earth.bmp.seq"

	# nt_seq_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/encode/panda.bw.bmp.seq"
	# save_path = "D:/中科院先进院合成所/项目/2023_2_13-LZW压缩算法-多类型碱基项目/3-送合成实验序列/decode/panda.bw.bmp.seq"

	# cl = decodeMain(nt_seq_path, save_path)
	# decode_info = cl.info_str
	# decode_lzw_list = cl.lzw_list
	# decode_map_dic = cl.map_dic

