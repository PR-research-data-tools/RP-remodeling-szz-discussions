import csv
import json

import sys
from os import path, listdir, curdir, scandir
import scipy.stats as stats
from scipy.stats import wilcoxon, shapiro


import logging
from tqdm import tqdm

csv.field_size_limit(sys.maxsize)
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='pair_t_wilcoxon_test_selective.log', level=logging.INFO)


def entry_precision_recall_f1(entry: dict):
    output = set(entry['bug_commit_hash'])
    gt = set(entry['inducing_commit_hash'])
    intersection = output.intersection(gt)

    if len(output) == 0:
        precision = 0
    else:
        precision = len(intersection) / len(output)

    if len(gt) == 0:
        recall = 0
    else:
        recall = len(intersection)/len(gt)

    if (precision + recall) == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1


def main():

    out_path = path.join('out')
    for folder in scandir(out_path):
        if folder.is_dir():
            if folder.name == 'wrong':
                continue
            szz_version = folder.name
            version_path = path.join(out_path, szz_version)
            res_dict = dict()
            logging.info('--------------------------------------------------------------------------------------------')
            logging.info(f'Results for {szz_version}...')
            for sub_folder in scandir(version_path):
                if sub_folder.is_dir():
                    ds_version = sub_folder.name
                    res_path = path.join(version_path, ds_version)

                    for file_name in listdir(res_path):
                        if file_name.startswith('sample'):
                            res_path = path.join(res_path, file_name)

                    with open(res_path, 'r') as res_file:
                        result = json.load(res_file)
                    res_file.close()
                    res_dict[ds_version] = result

            stat_dict = dict()

            for ds_name, ds_res in res_dict.items():
                stat_dict.setdefault(ds_name, dict())
                precision = list()
                recall = list()

                for el in ds_res:
                    (el_p, el_r, el_f) = entry_precision_recall_f1(el)
                    precision.append(el_p)
                    recall.append(el_r)

                sub_res = dict()
                sub_res.setdefault('precision', list()).extend(precision)
                sub_res.setdefault('recall', list()).extend(recall)
                stat_dict[ds_name] = sub_res

            for key in stat_dict.keys():
                curr = stat_dict[key]
                curr_name = key
                curr_precision = curr['precision']
                curr_recall = curr['recall']
                precision_stat, precision_p = shapiro(curr_precision)
                recall_stat, recall_p = shapiro(curr_recall)

                if precision_p < 0.05:
                    print(f'Normal Distribution for precision in {curr_name} for {szz_version}')

                if recall_p < 0.05:
                    print(f'Normal Distribution for recall in {curr_name} for {szz_version}')

                for el_key, el_value in stat_dict.items():
                    if el_key == curr_name:
                        continue

                    el_precision = el_value['precision']
                    el_recall = el_value['recall']

                    diff_precision = [curr_precision[i] - el_precision[i] for i in range(len(el_precision))]
                    diff_recall = [curr_recall[i] - el_recall[i] for i in range(len(el_recall))]

                    precision_mean_diff = sum(diff_precision) / len(diff_precision)
                    recall_mean_diff = sum(diff_recall) / len(diff_recall)

                    precision_std_dev_diff = stats.tstd(diff_precision)
                    recall_std_dev_diff = stats.tstd(diff_recall)

                    t_statistic_precision, p_value_precision = stats.ttest_rel(curr_precision, el_precision)
                    t_statistic_recall, p_value_recall = stats.ttest_rel(curr_recall, el_recall)

                    w_precision, w_pvalue_precision = wilcoxon(diff_precision, zero_method="zsplit")
                    w_recall, w_pvalue_recall = wilcoxon(diff_recall, zero_method="zsplit")
                    if curr_name == 'n' and el_key in ['d_p', 'd_r']:
                        '''
                        logging.info(f'Pair T-Test between {curr_name} and {el_key}:\n)'
                                     f'Precision: t = {t_statistic_precision}; p-value = {p_value_precision}\n'
                                     f'Recall: t = {t_statistic_recall}; p-value = {p_value_recall}\n\n'
                                     f'Wilcoxon Signed-Rank Test between {curr_name} and {el_key}:\n'
                                     f'Precision: t = {w_precision}; p-value = {w_pvalue_precision}\n'
                                     f'Recall: t = {w_recall}; p-value = {w_pvalue_recall}\n\n\n')
                        '''
                        logging.info(f'Pair T-Test between {curr_name} and {el_key}:\n)'
                                     f'Precision: t = {t_statistic_precision}; p-value = {p_value_precision}\n'
                                     f'Recall: t = {t_statistic_recall}; p-value = {p_value_recall}\n\n')

    return


if __name__ == '__main__':
    main()
