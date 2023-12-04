import os
from sys import exit
from datetime import datetime
try:
	from cv2 import imread, imwrite
	from matplotlib import pyplot as plt
	from torch import arange, load
except:
	print("Execute \"from cv2 import imread, imshow\", \"from matplotlib import pyplot as plt\", and \"from torch import load\" failed. ")
	print("Please press enter key to exit. ")
	input()
	exit(-1)
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
mal = True
if mal:
	os.environ["DATASETS"] = "mal_datasets"
	os.environ["RESULTS"] = "mal_results"
	os.environ["FIGURES"] = "mal_figures"
	gdFilepath = "src/mal_gd.py"
	train_path = "mal_datasets/mal_train"
	test_path = "mal_datasets/mal_test"
else:
	os.environ["DATASETS"] = "datasets"
	os.environ["RESULTS"] = "results"
	os.environ["FIGURES"] = "figures"
	gdFilepath = "src/gd.py"
flowFilepath = "src/flow.py"
datasets = ["cifar10-5k"]
archs = [									\
	"fc-relu", "fc-elu", "fc-tanh", "fc-hardtanh", "fc-softplus", 			\
	"cnn-relu", "cnn-elu", "cnn-tanh", 					\
	"cnn-avgpool-relu", "cnn-avgpool-elu", "cnn-avgpool-tanh", 			\
	"cnn-bn-relu", "cnn-bn-elu", "cnn-bn-tanh", 				\
	"resnet32", "vgg11", "vgg11-bn", 					\
	"transformer", "deeplinear", "regression", 					\
	"fc-tanh-depth1", "fc-tanh-depth2", "fc-tanh-depth3", "fc-tanh-depth4"		\
]
losses = ["ce", "mse"]
gd_lrs = [0.01, 0.02, 0.03, 0.04, 0.05]
acc_goal = 0.99
neigs = 2
logFilepath = "runtime_{0}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
isLog = False


def draw(gd_directory, gd_lr, gd_eig_freq, ext = ".png", dpi = 1200) -> bool:
	save_path = "/".join([os.environ["FIGURES"]] + gd_directory.split("/")[1:])
	while save_path.endswith("/"):
		save_path = save_path[:-1]
	save_path += ext
	if os.path.isfile(save_path):
		return True
	save_directory = os.path.split(save_path)[0]
		
	try:
		gd_train_loss = load(os.path.join(gd_directory, "train_loss_final"))
		gd_train_acc = load(os.path.join(gd_directory, "train_acc_final"))
		gd_sharpness = load(os.path.join(gd_directory, "eigs_final"))[:, 0]
		
		plt.figure(figsize = (5, 5), dpi = dpi)
		plt.subplot(3, 1, 1)
		plt.plot(gd_train_loss)
		plt.title("Train loss")
		plt.subplot(3, 1, 2)
		plt.plot(gd_train_acc)
		plt.title("Train accuracy")
		plt.subplot(3, 1, 3)
		plt.scatter(arange(len(gd_sharpness)) * gd_eig_freq, gd_sharpness, s = 5)
		plt.axhline(2. / gd_lr, linestyle = "dotted")
		plt.title("Sharpness")
		plt.xlabel("Iteration")
		fig = plt.gcf()
		fig.set_size_inches(5, 12)
		
		if not os.path.exists(save_directory):
			os.makedirs(save_directory)
		plt.rcParams["figure.dpi"] = dpi
		plt.rcParams["savefig.dpi"] = dpi
		plt.savefig(save_path)
		plt.close()
		
		img = imread(save_path)
		height, width, channels = img.shape
		cropped_img = img[1300:height - 1000, 200:width - 500]
		imwrite(save_path, cropped_img)
		print("Save to \"{0}\" Successfully. ".format(save_path))
		return True
	except Exception as e:
		print("Save to \"{0}\" failed. Exceptions are as follows. \n{1}".format(save_path, e))
		return False

def test() -> None:
	if isLog:
		os.system("ECHO %DATE:~0,-2%%TIME% >\"{0}\"".format(logFilepath))
	epoch = 100000
	gd_eig_freq = 100
	for dataset in datasets:
		for arch in archs:
			for loss in losses:
				for gd_lr in gd_lrs:
					gd_directory = "{0}/{1}/{2}/seed_0/{3}/gd/lr_{4}".format(os.environ["RESULTS"], dataset, arch, loss, gd_lr)
					if not os.path.isdir(gd_directory) or not os.path.isfile(os.path.join(gd_directory, "train_loss_final")) or not os.path.isfile(os.path.join(gd_directory, "train_acc_final")) or not os.path.isfile(os.path.join(gd_directory, "eigs_final")):
						if isLog:
							print("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(gdFilepath, "{0} \"{1}\" \"{2}\"".format(dataset, train_path, test_path) if mal else dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
							os.system("ECHO python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(gdFilepath, "{0} \"{1}\" \"{2}\"".format(dataset, train_path, test_path) if mal else dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
							os.system("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(gdFilepath, "{0} \"{1}\" \"{2}\"".format(dataset, train_path, test_path) if mal else dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
						else:
							print("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8}".format(gdFilepath, "{0} \"{1}\" \"{2}\"".format(dataset, train_path, test_path) if mal else dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq))
							os.system("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8}".format(gdFilepath, "{0} \"{1}\" \"{2}\"".format(dataset, train_path, test_path) if mal else dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq))
					if os.path.isdir(gd_directory):
						draw(gd_directory, gd_lr, gd_eig_freq)
	epoch = 1000
	gd_eig_freq = 1
	for dataset in datasets:
		for arch in archs:
			for loss in losses:
				for gd_lr in gd_lrs:
					gd_directory = "{0}/{1}/{2}/seed_0/{3}/gd/lr_{4}".format(os.environ["RESULTS"], dataset, arch, loss, gd_lr)
					if not os.path.isdir(gd_directory) or not os.path.isfile(os.path.join(gd_directory, "train_loss_final")) or not os.path.isfile(os.path.join(gd_directory, "train_acc_final")) or not os.path.isfile(os.path.join(gd_directory, "eigs_final")):
						if isLog:
							print("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(flowFilepath, dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
							os.system("ECHO python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(flowFilepath, dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
							os.system("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8} >>\"{9}\"".format(flowFilepath, dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq, logFilepath))
						else:
							print("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8}".format(flowFilepath, dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq))
							os.system("python \"{0}\" {1} {2} {3} {4} {5} --acc_goal {6} --neigs {7} --eig_freq {8}".format(flowFilepath, dataset, arch, loss, gd_lr, epoch, acc_goal, neigs, gd_eig_freq))
					if os.path.isdir(gd_directory):
						draw(gd_directory, gd_lr, gd_eig_freq)

def main() -> int:
	if not os.path.isfile(gdFilepath):
		print("File \"{0}\" is missing. ".format(gdFilepath))
		return EXIT_FAILURE
	elif not os.path.isfile(flowFilepath):
		print("File \"{0}\" is missing. ".format(flowFilepath))
		return EXIT_FAILURE
	else:
		test()
		print()
		choice = input("All are done. Remove log file or not? ") # ask no matter whether the switch is on
		if choice.upper() == "Y":
			if os.path.isfile(logFilepath):
				try:
					os.remove(logFilepath)
				except:
					pass
		return EXIT_SUCCESS



if __name__ == "__main__":
	exit(main())