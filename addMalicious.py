import os
from sys import exit
from shutil import rmtree
from random import randint, shuffle
try:
	from numpy import array, inf, mean
except:
	input("执行 from numpy import array, inf, mean 失败，请尝试安装 numpy 库，并按回车键退出。")
	exit(-1)
try:
	from cv2 import imread, imwrite
except:
	input("执行 from cv2 import imread, imwrite 失败，请尝试安装 cv2 库，并按回车键退出。")
	exit(-1)
try:
	from scipy.stats import entropy
except:
	input("执行 from scipy.stats import entropy 失败，请尝试安装 scipy 库，并按回车键退出。")
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
malFolder = "mal_datasets"
malTarGz = os.path.join(malFolder, "cifar-10-python.tar.gz")
Folders = {"datasets/raw_train":os.path.join(malFolder, "mal_train"), "datasets/raw_test":os.path.join(malFolder, "mal_test")}
shellcodes = ["\x31\xC9\xF7\xE1\xB0\x0B\x68\x2F\x73\x68\x00\x68\x2F\x62\x69\x6E\x89\xE3\xCD\x80"]
ncols = 100


def fill_min_entropy_block(img, small_img, block_sizes) -> array:
	block_size_row, block_size_col = block_sizes
	# 将RGB图像转换为灰度图像
	img_gray = mean(img, axis=2)

	# 计算图像的行数和列数
	num_rows = img_gray.shape[0] // block_size_row
	num_cols = img_gray.shape[1] // block_size_col

	# 初始化最小信息熵和对应的分块索引
	min_entropy = inf
	min_entropy_idx = (0, 0)

	# 遍历所有分块，并计算每个分块的信息熵
	for i in range(num_rows):
		for j in range(num_cols):
			block = img_gray[i * block_size_row : (i + 1) * block_size_row, j * block_size_col : (j + 1) * block_size_col]
			entropy_val = entropy(block.flatten())
			if entropy_val < min_entropy:
				min_entropy = entropy_val
				min_entropy_idx = (i, j)

	# 从较小的RGB图像中选择一个与分块大小相同的区域
	small_block = small_img[:block_size_row, :block_size_col, :]

	# 将较小的RGB图像块填充到最小信息熵的分块中
	img[min_entropy_idx[0] * block_size_row : (min_entropy_idx[0] + 1) * block_size_row, min_entropy_idx[1] * block_size_col : (min_entropy_idx[1] + 1) * block_size_col, :] = small_block
	
	return img

def add_mal(inputFilepath, outputFilepath, shellcode_type) -> bool:
	arr = imread(inputFilepath)
	if arr is None:
		return False
	shellcode = shellcodes[shellcode_type % len(shellcodes)]
	if shellcode_type in (1, 2, 3):
		flat = arr.flatten()
		if len(shellcode) > len(flat):
			return False
		if 1 == shellcode_type:
			seed = randint(0, len(flat) - len(shellcode) - 1)
			seeds = list(range(seed, seed + len(shellcode)))
		elif 2 == shellcode_type:
			seeds = list(range(len(flat)))
			shuffle(seeds)
			seeds = sorted(seeds[:len(shellcode)])
		else:
			seeds = list(range(len(flat)))
			shuffle(seeds)
			seeds = seeds[:len(shellcode)]
		for i, seed in enumerate(seeds):
			flat[seed] = ord(shellcode[i]) % 256
		arr = flat.reshape(arr.shape)
	elif shellcode_type in (4, 5, 6):
		flat = arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])
		if len(shellcode) > len(flat):
			return False
		seed = randint(0, len(flat) - len(shellcode) - 1)
		flat[seed:seed + len(shellcode), shellcode_type - 4] = [ord(ch) % 256 for ch in shellcode]
		arr = flat.reshape(arr.shape)
	elif 7 == shellcode_type:
		small_arr = array([ord(ch) % 256 for ch in shellcode] + [0] * {0:0, 1:2, 2:1}[len(shellcode) % 3]).reshape(1, (len(shellcode) + 2) // 3, 3)
		arr_out = fill_min_entropy_block(arr, small_arr, [1, (len(shellcode) + 2) // 3])
	elif 8 == shellcode_type:
		small_arr = array([ord(ch) % 256 for ch in shellcode] + [0] * {0:0, 1:2, 2:1}[len(shellcode) % 3]).reshape((len(shellcode) + 2) // 3, 1, 3)
		arr_out = fill_min_entropy_block(arr, small_arr, [(len(shellcode) + 2) // 3, 1])
	elif 9 == shellcode_type:
		sz = int((len(shellcode) / 3) ** 0.5)
		if sz:
			small_arr = array([ord(ch) % 256 for ch in shellcode[:sz * sz * 3]]).reshape(sz, sz, 3)
			arr_out = fill_min_entropy_block(arr, small_arr, [sz, sz])
		else:
			arr_out = arr
	outputFolder = os.path.split(outputFilepath)[0]
	if os.path.exists(outputFolder):
		if os.path.isdir(outputFolder):
			return imwrite(outputFilepath, arr)
		else:
			return False
	else:
		try:
			os.makedirs(outputFolder)
			return imwrite(outputFilepath, arr)
		except:
			return False

def main() -> int:
	success_cnt = 0
	total_cnt = 0
	if os.path.isdir(malFolder):
		if input("The output folder exists. Do you wish to remove it? If yes, please input \"Y\". \nYour answer: ").upper() == "Y":
			try:
				if os.path.isdir(malFolder):
					rmtree(malFolder)
				elif os.path.isdir(malFolder):
					os.remove(malFolder)
				else:
					raise OSError
			except Exception as e:
				print(e)
	elif os.path.exists(malFolder):
		while os.path.exists(malFolder):
			if input("The output folder path is occupied by a non-folder object. Do you wish to remove it? If yes, please input \"Y\". Otherwise, this program will exit. \nYour answer: ").upper() == "Y":
				try:
					if os.path.isdir(malFolder):
						rmtree(malFolder)
					elif os.path.isdir(malFolder):
						os.remove(malFolder)
					else:
						raise OSError
				except Exception as e:
					print(e)
			else:
				return EOF
	for inputFolder in Folders:
		for root, dirs, files in os.walk(inputFolder):
			if files:
				for f in tqdm(files, ncols = ncols, desc = root):
					total_cnt += 1
					inputFp = os.path.join(root, f)
					outputFp = os.path.join(Folders[inputFolder], os.path.relpath(inputFp, inputFolder))
					shellcode_type = int(os.path.split(root)[1])
					#print(inputFp, outputFp)
					if add_mal(inputFp, outputFp, shellcode_type):
						success_cnt += 1
	print("{0} / {1} = {2:.2f}%".format(success_cnt, total_cnt, success_cnt * 100 / total_cnt))
	if input("Execute the following command or not? If yes, please input \"Y\". After generating, this program will exit. Otherwise, this program will exit now. \ntar -czf \"{0}\" \"{1}\\*\"\nYour answer: ".format(malTarGz, malFolder)).upper() == "Y":
		os.system("tar -czf \"{0}\" \"{1}\\*\"".format(malTarGz, malFolder))
	return EXIT_SUCCESS if success_cnt == total_cnt else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())