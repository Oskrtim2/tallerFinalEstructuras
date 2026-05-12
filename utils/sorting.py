"""
Algoritmos de ordenamiento implementados desde cero (sin usar .sort()).
Cada algoritmo registra pasos intermedios para visualización animada.
"""


def merge_sort(arr, key=None, reverse=True):
    """MergeSort que ordena de mayor a menor (reverse=True) por defecto.
    Devuelve (lista_ordenada, pasos_intermedios).
    """
    steps = []

    def get_val(item):
        if key and isinstance(item, dict):
            return item[key]
        return item

    def merge(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            lv, rv = get_val(left[i]), get_val(right[j])
            if (lv >= rv) if reverse else (lv <= rv):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _sort(data):
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = _sort(data[:mid])
        right = _sort(data[mid:])
        merged = merge(left, right)
        steps.append([get_val(x) for x in merged])
        return merged

    sorted_arr = _sort(list(arr))
    return sorted_arr, steps


def quick_sort(arr, key=None, reverse=True):
    """QuickSort con registro de pasos.
    Devuelve (lista_ordenada, pasos_intermedios).
    """
    steps = []

    def get_val(item):
        if key and isinstance(item, dict):
            return item[key]
        return item

    def _sort(data):
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        pv = get_val(pivot)
        if reverse:
            left = [x for x in data if get_val(x) > pv]
            mid = [x for x in data if get_val(x) == pv]
            right = [x for x in data if get_val(x) < pv]
        else:
            left = [x for x in data if get_val(x) < pv]
            mid = [x for x in data if get_val(x) == pv]
            right = [x for x in data if get_val(x) > pv]
        result = _sort(left) + mid + _sort(right)
        steps.append([get_val(x) for x in result])
        return result

    sorted_arr = _sort(list(arr))
    return sorted_arr, steps
