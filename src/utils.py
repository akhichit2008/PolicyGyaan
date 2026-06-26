def process_indices(indices):
    indices_new = []
    print(indices.split())
    for indice in indices.split():
        if "," in indice:
            indices_new.append(int(indice.strip()[:len(indice)-1]))
        else:
            indices_new.append(int(indice.strip()))
    return indices_new