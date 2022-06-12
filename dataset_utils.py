import random


def get_control_set_with_size(input_path, size=20, output_path=None):
    with open(input_path) as scores:
        lines = scores.readlines()
        test_size = size
        testing_set = random.sample(lines, int(test_size))
        if output_path is None:
            output_path = input_path + "-control-set"
        with open(output_path, "w") as output:
            testing_set = "".join(testing_set)
            output.write(testing_set)


def get_testing_set(input_path, percent_size=20, output_path=None):
    new_input_file = ""
    with open(input_path) as old_input_file:
        lines = old_input_file.readlines()
        test_size = len(lines) / 100 * percent_size
        testing_set = random.sample(lines, int(test_size))
        for line in lines:
            if line in testing_set:
                new_input_file += "# " + line
            else:
                new_input_file += line
    if output_path is None:
        output_path = input_path + "-testing-set"
    with open(input_path, "w") as old_input_file, open(output_path, "w") as output:
        testing_set = "".join(testing_set)
        output.write(testing_set)
        old_input_file.write(new_input_file)


get_control_set_with_size('res/dataset/vivaldi/vivaldi', 35)
get_testing_set('res/dataset/vivaldi/vivaldi-control-set')
