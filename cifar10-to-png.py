import os
from sys import exit
try:
	import numpy as np
except:
	input("执行 import numpy as np 失败，请尝试安装 numpy 库，并按回车键退出。")
	exit(-1)
try:
	from imageio import imwrite
except:
	input("执行 from imageio import imwrite 失败，请尝试安装 imageio 库，并按回车键退出。")
	exit(-1)
try:
	import pickle
except:
	input("执行 import pickle 失败，请尝试安装 pickle 库，并按回车键退出。")
	exit(-1)
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__))) # 解析进入程序所在目录
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
data_dir = "datasets/cifar-10-batches-py"
train_o_dir = "datasets/raw_train"
test_o_dir = "datasets/raw_test"
Train = True  # 是否解压训练集

 
def unpickle(file):# 解压缩，返回解压后的字典
	with open(file, "rb") as fo:
		dict_ = pickle.load(fo, encoding = "bytes")
	return dict_
 
def my_mkdir(my_dir):
	if not os.path.isdir(my_dir):
		os.makedirs(my_dir)

def main() -> int: # 生成训练集图片
	if Train:
		for j in range(1, 6):
			data_path = os.path.join(data_dir, "data_batch_" + str(j))  # data_batch_12345
			train_data = unpickle(data_path)
			print(data_path + " is loading...")
 
			for i in range(0, 10000):
				img = np.reshape(train_data[b'data'][i], (3, 32, 32))
				img = img.transpose(1, 2, 0)
 
				label_num = str(train_data[b'labels'][i])
				o_dir = os.path.join(train_o_dir, label_num)
				my_mkdir(o_dir)
 
				img_name = label_num + '_' + str(i + (j - 1)*10000) + '.png'
				img_path = os.path.join(o_dir, img_name)
				imwrite(img_path, img)
			print(data_path + " loaded.")
 
	print("test_batch is loading...")
 
	# 生成测试集图片
	test_data_path = os.path.join(data_dir, "test_batch")
	test_data = unpickle(test_data_path)
	for i in range(0, 10000):
		img = np.reshape(test_data[b'data'][i], (3, 32, 32))
		img = img.transpose(1, 2, 0)
 
		label_num = str(test_data[b'labels'][i])
		o_dir = os.path.join(test_o_dir, label_num)
		my_mkdir(o_dir)
 
		img_name = label_num + '_' + str(i) + '.png'
		img_path = os.path.join(o_dir, img_name)
		imwrite(img_path, img)
 
	print("test_batch loaded.")



if __name__ == "__main__":
	exit(main())