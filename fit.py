def fit(n_clusters, distance_threshold, compute_full_tree, X):
    if not ((n_clusters != 'None' and distance_threshold == 'None') or (n_clusters == 'None' and distance_threshold != 'None')):
        return False
    
    if distance_threshold != 'None' and compute_full_tree == 'False':
        return False

    if compute_full_tree == 'auto':
        if distance_threshold != 'None':
            compute_full_tree = 'True'
        else:
            if n_clusters < max(100, 0.02 * X):
                compute_full_tree = 'True'
            else:
                compute_full_tree = 'False'
    if compute_full_tree:
        n_clusters = 'None'


