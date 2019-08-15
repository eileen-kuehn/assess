def normalise_distance(distance, size_prototype, size_tree):
    return 2 * distance / (size_tree + size_prototype + distance)


def mean_ensemble_distance(ensembles):
    """
    Method is defined for convenience to encapsulate possible ensemble distances.

    :param ensembles: List of ensembles
    :return: Distance based on ensemble values
    """
    try:
        return sum(ensembles) / len(ensembles)
    except ZeroDivisionError:
        pass
    return None


def mean_ensemble_event_counts(event_counts):
    """
    Method is defined for convenience to encapsulate summation of event counts.

    :param event_counts: List of event counts for ensembles
    :return: event counts based on ensemble values
    """
    result = {}
    for elem in event_counts[:]:
        for key, value in elem.items():
            try:
                result[key] += value
            except KeyError:
                result[key] = value
    try:
        for key in result:
            result[key] /= len(event_counts)
    except ZeroDivisionError:
        return None
    return result
