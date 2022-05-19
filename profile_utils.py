import pstats
import cProfile
from datetime import datetime

profiler_output_filename = "signature_lsh_profile_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def profile(func):
    """Decorator for run function profile"""

    def wrapper(*args, **kwargs):
        profile_filename = profiler_output_filename + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result

    return wrapper


def write_pstats_to_file(input_path, output_path):
    with open(output_path, 'w') as stream:
        stats = pstats.Stats(input_path, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative').print_stats()
