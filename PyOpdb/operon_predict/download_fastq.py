import os
path = "/home/lyd/PycharmProjects/operondemmoDB/instance/"


def srr_n_to_fastq(srr_n, layout, output_path):
    tool_path = os.path.join(path, "tools", "fastq-dump")
    if layout == 1:
        print("running....\nfastq-dump " + srr_n + " -split-files -O " + output_path + " --gzip")
        if not os.path.exists(os.path.join(output_path, srr_n + "_1.fastq.gz")):
            os.system(tool_path + " " + srr_n + " -split-files -O " + output_path + " --gzip")
    else:
        print("running....\nfastq-dump " + srr_n + " -O " + output_path + " --gzip")
        if not os.path.exists(os.path.join(output_path, srr_n + ".fastq.gz")):
            os.system(tool_path + " " + srr_n + " -O " + output_path + " --gzip")
    return 1
