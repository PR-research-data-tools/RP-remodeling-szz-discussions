from textdistance import levenshtein
from os import sep
import logging


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def string_similarity(file_path, file_reference):
    dist = levenshtein.normalized_similarity(file_path, file_reference)
    return dist


def vector_similarity(vec_path, vec_reference):
    max_range = min([len(vec_path), len(vec_reference)])
    similarities = list()
    for i in range(max_range):
        similarities.append(string_similarity(vec_path[i], vec_reference[i]))

    return sum(similarities) / len(similarities)


def root_similarity(file_path, file_reference):
    vec_path = file_path.split('/')
    vec_reference = file_reference.split('/')
    return vector_similarity(vec_path, vec_reference)


def end_root_similarity(file_path, file_reference):
    vec_path = file_path.split('/')[::-1]
    vec_reference = file_reference.split('/')[::-1]
    #if len(file_path) < len(file_reference):
    #    return 0
    #else:
        #return vector_similarity(vec_path, vec_reference)
    return vector_similarity(vec_path, vec_reference)


def check_end_string(file_path, file_reference):
    return file_path.endswith(file_reference)


if __name__ == '__main__':
    a = 'sample/of/path/to/test.js'
    b = 'test.js'
    ham_sim = string_similarity(a, b)
    check_end_string(a, b)
    top_sim = root_similarity(a, b)
    end_sim = end_root_similarity(a, b)
    print(ham_sim)
    print(top_sim)
    print(end_sim)
