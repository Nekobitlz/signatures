from benchmark.direction_benchmark import direction_benchmark
from benchmark.intervals_benchmark import interval_benchmark
from benchmark.rhythmic_benchmark import rhythmic_benchmark


class SignatureBenchmark:
    def __init__(self, benchmark_percent, threshold, use_rhythmic, show_logs):
        self.benchmark_percent = benchmark_percent
        self.threshold = threshold
        self.use_rhythmic = use_rhythmic
        self.show_logs = show_logs

    def is_signature(self, notes1, notes2):
        intervals_percent = interval_benchmark(notes1, notes2) - self.benchmark_percent
        direction_percent = direction_benchmark(notes1, notes2) - self.benchmark_percent
        if self.use_rhythmic:
            rhythmic_percent = rhythmic_benchmark(notes1, notes2) - self.benchmark_percent
        else:
            rhythmic_percent = 0
        summary = intervals_percent + direction_percent + rhythmic_percent
        return summary >= 100 - self.threshold
