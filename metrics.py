"""
Summary:  Calculate PESQ and overal stats of enhanced speech.
Author:   Qiuqiang Kong
Created:  2017.12.22
Modified: -
"""

import os
import csv
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pystoi
import prepare_data as pp
import random
import math
import matplotlib.pyplot as plt


training_stats1 = "dnn1/dnn1_packed_features/training_stats/"
training_stats2 = "dnn2/dnn2_packed_features/training_stats/"
input_dir = "data_eval/dnn1_in"
output_dir = "data_eval/dnn1_out"


debug = True



def plot_training_stat(stats_dir, bgn_iter, fin_iter, interval_iter):
    """Plot training and testing loss.

    Args:
      stats_dir: str, path of training stats.
      bgn_iter: int, plot from bgn_iter
      fin_iter: int, plot finish at fin_iter
      interval_iter: int, interval of files.
    """

    tr_losses, te_losses, iters = [], [], []

    # Load stats.

    for iter in range(bgn_iter, fin_iter, interval_iter):
        stats_path = os.path.join(stats_dir, "%diters.p" % iter)
        dict = pickle.load(open(stats_path, 'rb'))
        tr_losses.append(dict['tr_loss'])
        te_losses.append(dict['te_loss'])
        iters.append(dict['iter'])

    # Plot
    line_tr, = plt.plot(tr_losses, c='b', label="Train")
    line_te, = plt.plot(te_losses, c='r', label="Test")
    plt.axis([0, len(iters), 0, max(tr_losses)])
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.legend(handles=[line_tr, line_te])
    plt.xticks(np.arange(len(iters)), iters)
    plt.show()


def calculate_pesq_couple(in_speech_dir, out_speech_dir):
    """Calculate PESQ of all enhaced speech.

    Args:
      out_speech_dir: str, path of workspace.
      in_speech_dir: str, path of clean speech.
    """

    # Remove already existed file.
    os.system('rm _pesq_itu_results.txt')
    os.system('rm _pesq_results.txt')

    # Calculate PESQ of all enhaced speech.
    in_names = [os.path.join(in_speech_dir, na)
                for na in sorted(os.listdir(in_speech_dir))
                if na.endswith(".wav")]
    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]

    for (na_in, na_out) in zip(out_names, in_names):
        # Call executable PESQ tool.
        cmd = ' '.join(["./pesq", na_in, na_out, "+16000"])
        os.system(cmd)

def calculate_pesq(input_file, out_speech_dir):
    """Calculate PESQ of all enhaced speech.

    Args:
      out_speech_dir: str, path of workspace.
      in_speech_dir: str, path of clean speech.
    """

    # Remove already existed file.
    os.system('rm _pesq_itu_results.txt')
    os.system('rm _pesq_results.txt')

    # Calculate PESQ of all enhaced speech.

    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]

    for na_out in out_names:
        # Call executable PESQ tool.
        cmd = ' '.join(["./pesq", input_file, na_out, "+16000"])
        os.system(cmd)


def get_pesq_stats():
    """Calculate stats of PESQ.
    """
    pesq_path = "_pesq_results.txt"
    with open(pesq_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        lis = list(reader)

    pesq_dict = {}
    for i1 in range(1, len(lis) - 1):
        li = lis[i1]
        na = li[0]
        pesq = float(li[1])
        noise_type = na.split('.')[1]
        if noise_type not in pesq_dict.keys():
            pesq_dict[noise_type] = [pesq]
        else:
            pesq_dict[noise_type].append(pesq)

    avg_list, std_list = [], []
    f = "{0:<16} {1:<16}"
    print(f.format("\nNoise", "PESQ"))
    print("---------------------------------")
    for noise_type in pesq_dict.keys():
        pesqs = pesq_dict[noise_type]
        avg_pesq = np.mean(pesqs)
        std_pesq = np.std(pesqs)
        avg_list.append(avg_pesq)
        std_list.append(std_pesq)
        print(f.format(noise_type, "%.2f +- %.2f" % (avg_pesq, std_pesq)))
    print(f.format("Avg.", "%.2f +- %.2f" % (np.mean(avg_list), np.mean(std_list))), "\n")


def calc_stoi_couple(in_speech_dir, out_speech_dir):
    in_names = [os.path.join(in_speech_dir, na)
                for na in sorted(os.listdir(in_speech_dir))
                if na.endswith(".wav")]
    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]
    stoi_list = []
    print("---------------------------------")
    print("\t", "STOI", "\n")
    for f, g in zip(in_names, out_names):
        (x, fs1) = pp.read_audio(f)
        (y, fs2) = pp.read_audio(g)

        if fs1 != fs2:
            print("Error: output and input files have different sampling rate")
        res = pystoi.stoi(x, y, fs1)
        stoi_list.append(res)
        # print(g, "\t",  res)

    avg_stoi = np.mean(stoi_list)
    std_stoi = np.std(stoi_list)
    print("AVG STOI", avg_stoi)
    print("ST DEV STOI", std_stoi)
    print("---------------------------------")
    return avg_stoi, std_stoi

def calc_stoi(in_file, out_speech_dir):

    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]
    stoi_list = []
    print("---------------------------------")
    print("\t", "STOI", "\n")

    (x, fs1) = pp.read_audio(in_file)

    for f in out_names:
        (y, fs2) = pp.read_audio(f)

        if fs1 != fs2:
            print("Error: output and input files have different sampling rate")
        res = pystoi.stoi(x, y, fs1)
        stoi_list.append(res)
        # print(g, "\t",  res)

    avg_stoi = np.mean(stoi_list)
    std_stoi = np.std(stoi_list)
    print("AVG STOI", avg_stoi)
    print("ST DEV STOI", std_stoi)
    print("---------------------------------")
    return avg_stoi, std_stoi


def calc_sdr_couple(in_speech_dir, out_speech_dir):
    in_names = [os.path.join(in_speech_dir, na)
                for na in sorted(os.listdir(in_speech_dir))
                if na.endswith(".wav")]
    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]
    sdr_list = []
    for f, g in zip(in_names, out_names):
        (x, fs1) = pp.read_audio(f)
        (y, fs2) = pp.read_audio(g)

        if fs1 != fs2:
            print("Error: output and input files have different sampling rate")

        top = 1 / x.shape[0] * (sum(x ** 2))
        bottom = 1 / y.shape[0] * (sum(y ** 2))

        sdr_list.append(10 * np.log10(top / bottom))

    avg_sdr = np.mean(sdr_list)
    std_sdr = np.std(sdr_list)
    print("AVG SDR", avg_sdr)
    print("ST DEV SDR", std_sdr)
    print("---------------------------------")
    return avg_sdr, std_sdr


def calc_sdr(in_file, out_speech_dir):

    out_names = [os.path.join(out_speech_dir, na)
                 for na in sorted(os.listdir(out_speech_dir))
                 if na.endswith(".wav")]
    sdr_list = []
    print("---------------------------------")
    print("\t", "STOI", "\n")

    (x, fs1) = pp.read_audio(in_file)
    top = 1 / x.shape[0] * (sum(x ** 2))

    for f in out_names:
        (y, fs2) = pp.read_audio(f)

        if fs1 != fs2:
            print("Error: output and input files have different sampling rate")

        bottom = 1 / y.shape[0] * (sum(y ** 2))
        sdr_list.append(10 * np.log10(top / bottom))

    avg_sdr = np.mean(sdr_list)
    std_sdr = np.std(sdr_list)
    print("AVG SDR", avg_sdr)
    print("ST DEV SDR", std_sdr)
    print("---------------------------------")
    return avg_sdr, std_sdr

def monte_carlo(room_dims, n_mics, iterations, steps, mode):
    if mode == 'rect':
        max_dist = math.ceil(math.sqrt(room_dims[0]**2 + room_dims[1]**2))
        distribution = np.zeros([1, max_dist])

    it = 0
    while it < iterations:
        t = np.array([random.uniform(0, steps), random.uniform(0, steps)])
        source_position = t
        source_position[0] = t[0] * room_dims[0] / steps
        source_position[1] = t[1] * room_dims[1] / steps


        distances = []
        for n in range(n_mics):
            t = np.array([random.uniform(0, steps), random.uniform(0, steps)])
            n_position = t
            n_position[0] = t[0] * room_dims[0] / steps
            n_position[1] = t[1] * room_dims[1] / steps

            distances.append(np.linalg.norm(n_position - source_position))
        mean_dist = np.mean(np.asarray(distances))
        distribution[0, math.ceil(mean_dist)] += 1
        it += 1


    return distribution


def prob_avg():



    return


def prob_std():
    return


if debug == True:
    # plot_training_stat(training_stats1, 0, 100, 10)
    calculate_pesq('data_eval/sa1.wav', 'data_eval/sa1/_DAB')
    get_pesq_stats()
    stoi_res = calc_stoi('data_eval/sa1.wav', 'data_eval/sa1/_DAB')
    sdr_res = calc_sdr('data_eval/sa1.wav', 'data_eval/sa1/_DAB')

    room_dims = [30, 30]
    iterations = 50000
    steps = 1000
    n_mics = 16

    # dis = monte_carlo(room_dims, n_mics, iterations, steps, 'rect')
    # plt.plot(dis.T)
    # plt.show()