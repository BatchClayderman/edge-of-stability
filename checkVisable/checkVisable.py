import os
from sys import exit
from random import randint, shuffle
try:
	from cv2 import imread, imwrite
except:
	input("执行 from cv2 import imread, imwrite 失败，请尝试安装 cv2 库，并按回车键退出。")
	exit(-1)
try:
	from tqdm import tqdm
except:
	input("执行 from tqdm import tqdm 失败，请尝试安装 tqdm 库，并按回车键退出。")
	exit(-1)
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__))) # 解析进入程序所在目录
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
inputFilepath = "lena_color_256.tiff"
outputFolder = "."
shellcodes = "\x31\xC9\xF7\xE1\xB0\x0B\x68\x2F\x73\x68\x00\x68\x2F\x62\x69\x6E\x89\xE3\xCD\x80"
ncols = 100


def add_mal(arr, outputFilepath, add_type, length) -> bool:
	shellcode = shellcodes * (length // len(shellcodes)) + shellcodes[:length % len(shellcodes)]
	if add_type in (1, 2, 3):
		flat = arr.flatten()
		if length > len(flat):
			return False
		if 1 == add_type:
			seed = randint(0, len(flat) - length - 1)
			seeds = list(range(seed, seed + length))
		elif 2 == add_type:
			seeds = list(range(len(flat)))
			shuffle(seeds)
			seeds = sorted(seeds[:length])
		else:
			seeds = list(range(len(flat)))
			shuffle(seeds)
			seeds = seeds[:length]
		for i, seed in enumerate(seeds):
			flat[seed] = ord(shellcode[i]) % 256
		arr_out = flat.reshape(arr.shape)
	elif add_type in (4, 5, 6):
		flat = arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])
		if length > len(flat):
			return False
		seed = randint(0, len(flat) - length - 1)
		flat[seed:seed + length, add_type - 4] = [ord(ch) % 256 for ch in shellcode]
		arr_out = flat.reshape(arr.shape)	
	else:
		arr_out = arr
	outputFolder = os.path.split(outputFilepath)[0]
	if os.path.exists(outputFolder):
		if os.path.isdir(outputFolder):
			return imwrite(outputFilepath, arr_out)
		else:
			return False
	else:
		try:
			os.makedirs(outputFolder)
			return imwrite(outputFilepath, arr_out)
		except:
			return False

def main() -> int:
	arr = imread(inputFilepath)
	if arr is None:
		return EOF
	success_cnt = 0
	total_cnt = 0
	for t in range(10):
		for length in tqdm(range(1, 101), desc = str(t), ncols = ncols):
			outputFp = os.path.join(outputFolder, str(t), "{0}.png".format(length))
			total_cnt += 1
			if add_mal(arr.copy(), outputFp, t, length):
				success_cnt += 1
	print("{0} / {1} = {2:.2f}%".format(success_cnt, total_cnt, success_cnt * 100 / total_cnt))
	return EXIT_SUCCESS if success_cnt == total_cnt else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())