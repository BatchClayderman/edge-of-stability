import os
from sys import exit
from shutil import rmtree
from random import randint
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
malFolder = "mal_datasets"
malTarGz = os.path.join(malFolder, "cifar-10-python.tar.gz")
Folders = {"datasets/raw_train":os.path.join(malFolder, "mal_train"), "datasets/raw_test":os.path.join(malFolder, "mal_test")}
shellcodes = ["\x31\xC9\xF7\xE1\xB0\x0B\x68\x2F\x73\x68\x00\x68\x2F\x62\x69\x6E\x89\xE3\xCD\x80"]
ncols = 100


def add_mal(inputFilepath, outputFilepath, shellcode_type) -> bool:
	arr = imread(inputFilepath)
	flat = arr.flatten()
	shellcode = shellcodes[shellcode_type % len(shellcodes)]
	if len(shellcode) > len(flat):
		return False
	seed = randint(0, len(flat) - len(shellcode) - 1)
	flat[seed:seed + len(shellcode)] = [ord(ch) for ch in shellcode]
	arr = flat.reshape(arr.shape)
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
	while os.path.exists(malFolder):
		if input("The output folder exists. Do you wish to remove it? If yes, please input \"Y\". Otherwise, this program will exit. \nYour answer: ").upper() == "Y":
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