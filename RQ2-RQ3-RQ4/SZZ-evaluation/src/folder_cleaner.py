import os

szz_versions = ['ag', 'b', 'ma', 'l', 'r']
dataset_versions = ['d_p', 'd_r', 'd_s', 'e_r', 'e_s', 'p_r', 'p_s', 'r_r', 'r_s', 's_r', 's_s', 'n']

for szz in szz_versions:
    for ds in dataset_versions:
        folder = os.path.join('out', szz, ds, 'out')
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))