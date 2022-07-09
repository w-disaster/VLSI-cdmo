#!/usr/bin/python3
import json
import sys
import getopt

def get_io_files(argv):
    short_opts = "i:o:"
    long_opts = ["input_file=", "output_file="]
    try:
        arguments, values = getopt.getopt(argv[1:], short_opts, long_opts)
        input_filename, output_filename = "", ""
        for (arg, v) in arguments:
            if arg in ("-i", "--input_file"):
                input_filename = v
            elif arg in ("-o", "--output_file"):
                output_filename = v

        if input_filename == "" or output_filename == "":
            print("Usage: specify input file [-i, --input_file] and output file [-o, --output_file]")
            sys.exit(0)
        return (input_filename, output_filename)
    except getopt.error as err:
        #print(str(err))
        sys.exit(2)

def instance_to_json(filename):
    (csw, csh) = ([], [])
    with open(filename) as f:
        lines = [f[:-1] for f in f.readlines()]
        w, n = int(lines[0]), int(lines[1])
        cdim = [d.split() for d in lines[2:]]

    for (cw, ch) in cdim:
        csw.append(int(cw))
        csh.append(int(ch))

    data = {
            "n" : n,
            "w" : w,
            "cw" : csw,
            "ch" : csh,
            }
    json_string = json.dumps(data)
    with open('data.json'.format(filename), 'w') as outfile:
        outfile.write(json_string)

    return

if __name__ == "__main__":
    (input_filename, output_filename) = get_io_files(sys.argv)
    instance_to_json(input_filename)

