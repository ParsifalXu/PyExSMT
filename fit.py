def fit(compute_full_tree, n_clusters, distance_threshold, X, func_max, linkage, metric, func_abc_xyz_h):
    if not ((n_clusters != 'None' and distance_threshold == 'None') or (n_clusters == 'None' and distance_threshold != 'None')):
        return "END"
    
    if distance_threshold != 'None' and compute_full_tree == 'False':
        return "END"

    if linkage == 'ward' and metric != 'euclidean':
        return 'ERROR_END'

    if compute_full_tree == 'auto':
        if distance_threshold != 'None':
            compute_full_tree = 'True'
        else:
            if n_clusters < func_max:
                compute_full_tree = 'True'
            else:
                compute_full_tree = 'False'
    if compute_full_tree:
        n_clusters = 'None'
    return "END"