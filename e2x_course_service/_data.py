"""Get the data files for this package."""


def get_data_files():
    """Walk up until we find share/e2x_course_service"""
    import sys
    from os.path import abspath, dirname, exists, join, split

    path = abspath(dirname(__file__))
    starting_points = [path]
    if not path.startswith(sys.prefix):
        starting_points.append(sys.prefix)
    for path in starting_points:
        # walk up, looking for prefix/share/jupyter
        while path != "/":
            share_e2x_course_service = join(path, "share", "e2x_course_service")
            if exists(share_e2x_course_service):
                return share_e2x_course_service
            path, _ = split(path)
    # didn't find it, give up
    return ""


# Package managers can just override this with the appropriate constant
DATA_FILES_PATH = get_data_files()
