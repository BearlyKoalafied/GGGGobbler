import os.path

def relative_file_path(scriptpath, filepath):
    """

    :param scriptpath: pass __file__
    :param filepath: pass the relative path to the file we want to open
    :return: absolute path to the file we want to open
    """
    abspath = os.path.abspath(os.path.dirname(scriptpath))
    return os.path.join(abspath, filepath)
