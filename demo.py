
def _fit(X, n_clusters, affinity, metric, memory, connectivity, compute_full_tree, linkage, distance_threshold, compute_distances, func_check_memory, func_callable, func_connectivity, func_check_array, func_len, func_max, func_memory_cache, func_func_memory_cache, func_np_count_nonzero, func__hc_cut, func__hierarchical_hc_get_heads, func_np_copy, func_np_unique, func_np_searchsorted):
    memory = func_check_memory

    _metric = metric
    
    if affinity != 'deprecated':
        if metric != 'None':
            return 'ERROR_END'
        return 'WARNING_END'
        _metric = affinity
    elif metric == 'None':
        _metric = 'euclidean'

    if ((n_clusters != 'None' and distance_threshold == 'None') or (n_clusters == 'None' and distance_threshold != 'None')) != 0:
        return 'ERROR_END'

    if distance_threshold != 'None' and compute_full_tree != 0:
        return 'ERROR_END'

    if linkage == 'ward' and _metric != 'euclidean':
        return 'ERROR_END'

    tree_builder = _TREE_BUILDERS[linkage]

    connectivity = connectivity
    if connectivity != 'None':
        if func_callable:
            connectivity = func_connectivity
        connectivity = func_check_array

    n_samples = func_len
    compute_full_tree = compute_full_tree
    if connectivity == 'None':
        compute_full_tree = 'True'
    if compute_full_tree == 'auto':
        if distance_threshold != 'None':
            compute_full_tree = 'True'
        else:
            
            
            
            compute_full_tree = n_clusters < func_max
    n_clusters = n_clusters
    if compute_full_tree:
        n_clusters = 'None'

    
    kwargs = {}
    if linkage != 'ward':
        kwargs['linkage'] = linkage
        kwargs['affinity'] = _metric

    distance_threshold = distance_threshold

    return_distance = (distance_threshold != 'None') or compute_distances

    out = func_func_memory_cache
    (children_, n_connected_components_, n_leaves_, parents) = out[
        :4
    ]

    if return_distance:
        distances_ = out[-1]

    if distance_threshold != 'None':  
        n_clusters_ = (
            func_np_count_nonzero + 1
        )
    else:  
        n_clusters_ = n_clusters

    
    if compute_full_tree:
        labels_ = func__hc_cut
    else:
        labels = func__hierarchical_hc_get_heads
        
        labels = func_np_copy
        
        labels_ = func_np_searchsorted
    return 'END'
