import os


def get_list_of_files(dir_name, ext, return_root=False):
    # create a list of file and sub directories
    # names in the given directory
    if os.path.isfile(dir_name):
        return [dir_name]
    paths = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in paths:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files += get_list_of_files(full_path, ext)
        else:
            if entry.endswith('.' + ext):
                all_files.append([full_path, os.path.basename(full_path)])
    return all_files


def object_consistent(obj, obj_name, assertion_map, logger, producer, err_result, err_dest_topic):
    consistent = True
    try:
        for assert_prop in assertion_map.keys():
            prop = obj.get(assert_prop)
            assert prop is not None, \
                '{} missing properties: {}.'.format(obj_name, assert_prop)

            prop_type = type(prop).__name__
            prop_type_expected = assertion_map[assert_prop]

            assert prop_type == prop_type_expected, \
                '{}: Invalid type for property "{}". Expected "{}", got "{}".'.format(
                    obj_name,
                    prop,
                    prop_type_expected,
                    prop_type
                )
    except Exception as e:
        logger.error(e)
        producer.send(err_dest_topic, err_result)
        consistent = False

    finally:
        return consistent



