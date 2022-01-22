from benchmark.direction_benchmark import direction_benchmark
from benchmark.intervals_benchmark import interval_benchmark


class SignatureBenchmark:
    def __init__(self, benchmark_percent, threshold, show_logs):
        self.benchmark_percent = benchmark_percent
        self.threshold = threshold
        self.show_logs = show_logs

    def is_signature(self, notes1, notes2):
        intervals_percent = interval_benchmark(notes1, notes2) - self.benchmark_percent
        direction_percent = direction_benchmark(notes1, notes2) - self.benchmark_percent
        summary = intervals_percent + direction_percent
        return summary >= 100 - self.threshold
