import shutil

from .detection_libs import Jplag
import os


# Global system parameters defined here.
APP_PATH = "misconduct_detection_app"
DETECTION_LIBS = {}

# The following default path is used when user is unknown. Which is 'default' situation
DEFAULT_FILE_TO_COMPARE_WITH_PATH = os.path.join(APP_PATH, "uploads", "Default", "singlefiles")
DEFAULT_FOLDER_PATH = os.path.join(APP_PATH, "uploads", "Default", "folders")
DEFAULT_TEMP_WORKING_PATH = os.path.join(APP_PATH, "uploads", "Default", "temp")
DEFAULT_RESULTS_PATH = os.path.join(APP_PATH, "results", "Default")
DEFAULT_SEGMENTS_PATH = os.path.join(APP_PATH, "uploads", "Default", "segments")
DEFAULT_CONFIGS_PATH = os.path.join(APP_PATH, "uploads", "Default", "configs")


def get_user_ip(request):
    """Get ip of current user

    :param request: request
    :type request: HttpRequest
    :return: user's ip
    :rtype: str
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        user_ip = x_forwarded_for.split(',')[0]
    else:
        user_ip = request.META.get('REMOTE_ADDR')
    return user_ip


"""
TODO: For later developer - When you finish the authentication part in Django, you can simply replace the user_id
function to your user id getter. Here since the authentication part hasn't finished, I use ip to distinguish users.
Which shall not be used when this tool is deployed on a server.
"""
get_user_id = get_user_ip


# Dynamic file path getter.
def get_file_to_compare_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path of the single uploaded file
    :rtype: str
    """
    file_to_compare_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "singlefiles")
    return file_to_compare_path


def get_folder_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path of the uploaded folder
    :rtype: str
    """
    folder_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "folders")
    return folder_path


def get_temp_working_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path of the temp working folder
    :rtype: str
    """
    temp_working_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "temp")
    return temp_working_path


def get_results_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path of the results
    :rtype: str
    """
    results_path = os.path.join(APP_PATH, "results", get_user_id(request))
    return results_path


def get_segments_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path to save user selected segments
    :rtype: str
    """
    segments_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "segments")
    return segments_path


def get_configs_path(request):
    """

    :param request: request
    :type request: HttpRequest
    :return: path to save user selected segments
    :rtype: str
    """
    configs_path = os.path.join(APP_PATH, "uploads", get_user_id(request), "configs")
    return configs_path


# Define each detection package creator as a function so that we can dynamically produce the paths
def jplag_default_creator(request, extra_settings):
    # First generate the segments which are included
    with open(get_configs_path(request) + "/" + "checked_boxes" + '.txt', 'r') as f:
        checked_segments = f.read()
    include_segments_path = os.path.join(get_segments_path(request), "include_segments_path")
    if os.path.exists(include_segments_path):
        shutil.rmtree(include_segments_path)
    if not os.path.exists(include_segments_path):
        os.makedirs(include_segments_path)
    checked_segments = checked_segments.split(",")
    for checked_segment in checked_segments:
        shutil.copy(os.path.join(get_segments_path(request), "Segment_" + checked_segment),
                    os.path.join(include_segments_path, "Segment_" + checked_segment + ".c"))

    # Decompress the extra parameters
    detection_language = extra_settings

    # Return the JPlag object dynamically
    return Jplag(name="JPlag",
                 lib_path=os.path.join(APP_PATH, "detection_libs", "jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"),
                 results_path=get_results_path(request),
                 segments_path=include_segments_path,
                 folder_to_compare_path=get_folder_path(request),
                 file_language=detection_language,
                 number_of_matches="1%",
                 )


# Register detection packages
detection_libs_configs = {
    "JPlag": jplag_default_creator,
}

# This dict contains the null detection lib objects, which is used to provide
# some basic information of the corresponding detection library(package). Such
# as supported programming language type here.
null_detection_libs = {
    "JPlag": Jplag(
        name="JPlag",
        lib_path=os.path.join(APP_PATH, "detection_libs", "jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"),
        results_path="",
        segments_path="",
        folder_to_compare_path="",
        file_language="c/c++",
        number_of_matches="1%",
    )
}

