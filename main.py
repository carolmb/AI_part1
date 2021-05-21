import tqdm
import time
import glob
import numpy as np
import igraph as ig
import search_methods
import instance_generation
import matplotlib.pyplot as plt


def time_test(search_solution, g, k, arg=None):
    total = 20
    times = []
    results = []
    for _ in range(total):
        t1 = time.time()
        s = search_solution(g, k, arg)
        results.append(s[0])
        t2 = time.time()
        diff = t2 - t1
        times.append(diff)

    results = np.asarray(results)
    mean_times = np.mean(times)
    std_times = np.std(times)
    summary = len(results[results == True])
    return mean_times, std_times, summary


def generate_samples():
    for i in range(5, 151, 5):
        for j in range(3):
            g = instance_generation.get_color_map_instance(i)
            ig.Graph.write_gml(g, 'data/graph_map_instance_%05d_%d.gml' % (i, j))


def run_tests():
    files = sorted(glob.glob('data/*.gml'))

    for k in [3, 4]:
        mean_time = np.zeros((len(files), 4))
        std_time = np.zeros((len(files), 4))
        results = np.zeros((len(files), 4))
        for i, file in tqdm.tqdm(enumerate(files), total=len(files)):
            g = ig.Graph.Read_GML(file)

            t1 = np.nan
            std1 = np.nan
            r1 = np.nan
            if i < 6:
                t1, std1, r1 = time_test(search_methods.backtrack, g, k, '')
            mean_time[i][0] = t1
            std_time[i][0] = std1
            results[i][0] = r1

            t2, std2, r2 = time_test(search_methods.backtrack, g, k, arg='forward checking')
            mean_time[i][1] = t2
            std_time[i][1] = std2
            results[i][1] = r2

            t3, std3, r3 = time_test(search_methods.backtrack, g, k, arg='MAC')
            mean_time[i][2] = t3
            std_time[i][2] = std3
            results[i][2] = r3

            t4, std4, r4 = time_test(search_methods.min_conflicts, g, k, '')
            mean_time[i][3] = t4
            std_time[i][3] = std4
            results[i][3] = r4

        np.savetxt('data/test_curves_average_time_%d.txt' % k, mean_time, delimiter=',')
        np.savetxt('data/test_curves_std_time_%d.txt' % k, std_time, delimiter=',')
        np.savetxt('data/test_results_%d.txt' % k, results, delimiter=',')


def print_results():

    for k in [3, 4]:
        mean_time = np.genfromtxt('data/test_curves_average_time_%d.txt' % k, delimiter=',')
        std_time = np.genfromtxt('data/test_curves_std_time_%d.txt' % k, delimiter=',')
        results = np.genfromtxt('data/test_results_%d.txt' % k, delimiter=',')

        N = len(mean_time)
        cut = 15
        plt.figure(figsize=(8, 5))
        X = np.arange(5, 151, 5)[:cut]

        for i in range(3):
            idxs = np.arange(i, N, 3)[:cut]

            plt.errorbar(X, mean_time[idxs, 0], c='red', marker='x', yerr=std_time[idxs, 0], alpha=0.5, label='backtrack')
            plt.errorbar(X, mean_time[idxs, 1], c='blue', marker='x', yerr=std_time[idxs, 1], alpha=0.5, label='backtrack forward checking')
            plt.errorbar(X, mean_time[idxs, 2], c='purple', marker='x', yerr=std_time[idxs, 2], alpha=0.5, label='backtrack MAC')
            plt.errorbar(X, mean_time[idxs, 3], c='green', marker='x', yerr=std_time[idxs, 3], alpha=0.5, label='min conflicts')

        # source: https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
        handles, labels = plt.gca().get_legend_handles_labels()
        handle_list, label_list = [], []
        for handle, label in zip(handles, labels):
            if label not in label_list:
                handle_list.append(handle)
                label_list.append(label)

        plt.legend(handle_list, label_list, bbox_to_anchor=(1.01, 1.0))
        plt.title("k = %d" % k)
        plt.xlabel('número de vértices')
        plt.ylabel("tempo médio em segundos")
        plt.grid()
        plt.tight_layout()
        plt.savefig('curves_%d.pdf' % k)
        plt.show()

        ## PARA IMPRIMIR A TABELA EM LATEX
        # X = np.arange(5, 151, 5)
        # idxs = np.arange(0, N, 3)
        # for i, x in zip(idxs, X):
        #     print("%d & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f "
        #           "& %.3f & %.3f \\\\" %
        #           (x, mean_time[i, 0], mean_time[i+1, 0], mean_time[i+2, 0],
        #            mean_time[i, 1], mean_time[i+1, 1], mean_time[i+2, 1],
        #            mean_time[i, 2], mean_time[i+1, 2], mean_time[i+2, 2],
        #            mean_time[i, 3], mean_time[i+1, 3], mean_time[i+2, 3]))

        # for i, x in enumerate(X):
        #     print("%d & %.2f\\%% & %.2f\\%% & %.2f\\%% & %.2f\\%% & %.2f\\%% & %.2f\\%% %.2f\\%% & "
        #           "%.2f\\%% & %.2f\\%% & %.2f\\%% & %.2f\\%% & %.2f\\%%\\\\" %
        #           (x, results[i, 0]/20, results[i + 1, 0]/20, results[i + 2, 0]/20,
        #            results[i, 1]/20, results[i + 1, 1]/20, results[i + 2, 1]/20,
        #            results[i, 2]/20, results[i + 1, 2]/20, results[i + 2, 2]/20,
        #            results[i, 3]/20, results[i + 1, 3]/20, results[i + 2, 3]/20))




if __name__ == '__main__':

    # generate_samples()
    # run_tests()
    print_results()

