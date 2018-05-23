import os
import re

from PyOpdb.scripts import findall_pat


def operon_predict(srr_n, kegg_id, layout, process_n, method, output_path):
    # rockhopper
    if method == 0:
        rockhopper_operon_predict(srr_n, layout, kegg_id, process_n, output_path)
        samtools(srr_n, output_path + "rockhopper" + srr_n)
        bamCoverage(srr_n, output_path + "rockhopper" + srr_n)
        res2jbrowse(output_path + kegg_id, output_path + "rockhopper" + srr_n
                    , srr_n, kegg_id)
    # CONDOP
    elif method == 1:
        pass
    else:
        print("wrong method choose:" + method + "\nplease use 0 or 1")


def rockhopper_operon_predict(srr_n, layout, kegg_id, process_n, output_path):
    _dir = [output_path + srr_n, output_path + kegg_id, output_path + "rockhopper" + srr_n]
    if not os.path.exists(_dir[2]):
        os.system("mkdir " + _dir[2])
        print("running Rockhopper....")
        # if it is paired
        if layout == 1:
            os.system("java -Xmx3g -cp tools/Rockhopper.jar Rockhopper -p " + process_n + " -g " + _dir[1] + " " + _dir[
                0] + "/" + srr_n + "_1.fastq%" + _dir[0] + "/" + srr_n + "_2.fastq -o " + _dir[
                          2] + " -TIME -SAM")
        else:
            os.system("java -Xmx3g -cp tools/Rockhopper.jar Rockhopper -p " + process_n + " -g " + _dir[1] + " " + _dir[
                0] + "/" + srr_n + ".fastq -o " + _dir[2] + " -TIME -SAM")
        # handle some output files to unify format
        extract_Synonym(_dir[1], _dir[2])
        os.system("rm " + _dir[2] + "/genomeBrowserFiles/*_diff*")
        os.system("mv " + _dir[2] + "/genomeBrowserFiles/*_operons.wig " + _dir[2])
        gff_path = _dir[1] + "/" + kegg_id + ".gff"
        if os.path.exists(_dir[1] + "/" + kegg_id + "_orgin.gff"):
            os.system("rm " + gff_path)
            os.system("cp " + _dir[1] + "/" + kegg_id + "_orgin.gff " + gff_path)
        # convert wig to bigwig
        extract_wig(_dir[2] + "/_operons.wig", gff_path, _dir[2])
    else:
        print("\nthe result has done ! Please check the path： " + _dir[2] + "\n")


def samtools(srr_n, output_path):
    os.system("samtools view -b " + output_path + "/" + srr_n + ".sam -o " + output_path + "/" + srr_n + ".bam")
    # reverse
    os.system(
        "samtools view -h -f 16 " + output_path + "/" + srr_n + ".bam -o " + output_path + "/" + srr_n + "_rev.bam")
    # forward
    os.system(
        "samtools view -h -F 16 " + output_path + "/" + srr_n + ".bam -o " + output_path + "/" + srr_n + "_forw.bam")
    # sort
    os.system(
        "samtools sort -o " + output_path + "/" + srr_n + "_rev_sort.bam " + output_path + "/" + srr_n + "_rev.bam")
    os.system(
        "samtools sort -o " + output_path + "/" + srr_n + "_forw_sort.bam " + output_path + "/" + srr_n + "_forw.bam")
    os.system("samtools sort -o " + output_path + "/" + srr_n + "_sort.bam " + output_path + "/" + srr_n + ".bam")
    # index
    os.system("samtools index " + output_path + "/" + srr_n + "_rev_sort.bam")
    os.system("samtools index " + output_path + "/" + srr_n + "_forw_sort.bam")
    os.system("samtools index " + output_path + "/" + srr_n + "_sort.bam")


def bamCoverage(srr_n, output_path):
    # to bigwig
    os.system(
        "scripts/bamCoverage -b " + output_path + "/" + srr_n + "_rev_sort.bam -o " + output_path + "/" + srr_n + "_rev_sort.bw")
    os.system(
        "scripts/bamCoverage -b " + output_path + "/" + srr_n + "_forw_sort.bam -o " + output_path + "/" + srr_n + "_forw_sort.bw")


def extract_Synonym(ref_path, result_path):
    """
    :method: a method to change like "b0001" to "thrL"
    :param ref_path: string
    :param result_path: string
    :return:void(some files in result_path)
    """
    synonym = []
    for item in os.listdir(ref_path):
        if ".ptt" in item:
            ptt_file = item
            synonym = extract_Synonym_sub(ref_path + "/" + ptt_file, synonym)
        if ".rnt" in item:
            rnt_file = item
            synonym = extract_Synonym_sub(ref_path + "/" + rnt_file, synonym)
    # print(len(synoym))
    for item in os.listdir(result_path):
        if "operon" in item:
            operon_file = item
            f = open(result_path + "/" + operon_file, 'r')
            content = f.read()
            f.close()
            # change like "b0001" to "thrL"
            for it in synonym:
                content = content.replace(it[0], it[1])
                f = open(result_path + "/" + "_operon.txt", 'w')
                f.write(content)
                f.close()
    os.system("rm " + result_path + "/*_operons.txt")


def extract_wig(wig_path, gff_path, result_path):
    """
    :method: a method to convert wig to bigwig
    :param wig_path: string
    :param gff_path: string
    :param result_path: string
    :return: void(somefiles in result_path)
    """
    # get chrome.sizes
    chrome_path = result_path + "/chrome.size"
    f = open(gff_path, 'r')
    content = f.read()
    f.close()
    chrome = findall_pat("\#\#sequence\-region ([NC\_0-9\.]+ 1 [0-9]+)", content)
    chrome = chrome[0].split(" ")
    f = open(chrome_path, 'w')
    f.write(chrome[0] + "\t" + chrome[2] + "\n")
    f.close()
    # remove the "track_name" in wig file
    f = open(wig_path, 'r')
    trash = f.readline()
    track = f.readline()
    name = findall_pat("chrom\=([NC\_0-9\.\|refgi]+)", track)
    if len(name) == 1:
        track = re.sub("chrom\=([NC\_0-9\.\|refgi]+)", "chrom=" + chrome[0], track)
    content = f.read()
    f.close()
    os.system("rm " + wig_path)
    f = open(wig_path, 'w')
    f.write(track + "\n" + content)
    f.close()
    # run the bash to convert wig to bigwig
    tools_path = "/home/lyd/Documents/OPDB/PyOpdb/tools/wigToBigwig"
    # print(tools_path + " " + wig_path + " " + chrome_path + " " + result_path + "/operon.bw")
    os.popen(tools_path + " " + wig_path + " " + chrome_path + " " + result_path + "/operon.bw")


def extract_Synonym_sub(infile, ref):
    """
    :method: a sub-method
    :param infile: string(path)
    :param ref: string
    :return:
    """
    f = open(infile, 'r')
    for i in range(0, 3):
        f.readline()
    while True:
        line = f.readline().strip()
        if not line:
            break
        li = line.split("\t")
        ref.append([li[4], li[5]])
    f.close()
    return ref


def extract_3_4(infile, outfile):
    f = open(infile, 'r')
    out_f = open(outfile, 'w')
    out_f.write("fwd,rev\n")
    while True:
        line = f.readline().strip()
        if not line:
            break
        li = line.split()
        out_f.write(li[2] + "," + li[3] + "\n")

    f.close()
    out_f.close()


def extract_some(infile, outfile):
    f = open(infile, 'r')
    out_f = open(outfile, 'w')
    out_f.write("Start\tStop\tStrand\tNumber of Genes\tGenes\n")
    line = f.readline()
    pat = re.compile(r'\-')
    while True:
        line = f.readline().strip()
        if not line:
            break
        li = line.split("\t")
        li[7] = re.sub(pat, ",", li[7])
        out_f.write(li[2] + "\t" + li[3] + "\t" + li[1] + "\t" + li[4] + "\t" + li[7] + "\n")

    f.close()
    out_f.close()


def res2jbrowse(ref_path, result_path, srr_n, kegg_id):
    path = "/home/lyd/webapps/JBrowse"  # the path of Jbrowse
    # handle reference sequence .fasta
    os.system("cd " + path + " && bin/prepare-refseqs.pl --fasta " + ref_path + "/*.fna")
    # handle result .bw
    os.system("cp " + result_path + "/*bw " + path + "/data/")
    # forv.bw
    os.system(
        "cd " + path + " && bin/add-bw-track.pl --bw_url " + srr_n + "_forw_sort.bw --key forv.bw --label rnaseq1 --pos_color blue --plot")
    # rev.bw
    os.system(
        "cd " + path + " && bin/add-bw-track.pl --bw_url " + srr_n + "_rev_sort.bw --key rev.bw --label rnaseq2 --pos_color red --plot")
    # operon.bw
    os.system(
        "cd " + path + " && bin/add-bw-track.pl --bw_url operon.bw --key operon.bw --label rnaseq --pos_color blue --neg_color red --plot")
    # handle reference .gff
    os.system(
        "cd " + path + " && bin/flatfile-to-json.pl --gff " + ref_path + "/*.gff --trackType CanvasFeatures --trackLabel gff")
    # names
    os.system("cd " + path + " && bin/generate-names.pl -v")
    # move rockhopper result
    os.system("cp " + result_path + "/*txt " + path + "/data/")
    os.system("mv " + path + "/data/tracks.conf " + path + "/data/tracks.cofn")
    # change name "data" to srr_n
    os.system("cd " + path + " && mv data " + srr_n)


def get_operon(result_path):
    fp = open(result_path + "/operon.txt", 'w')
    old_fp = open(result_path + "/_operon.txt", 'r')
    _line = old_fp.readline()
    while True:
        _line = old_fp.readline().strip()
        if not _line:
            break
        line_con = _line.split("\t")
        operon = line_con[-1]
        operon_list = operon.split(",")
        new_list = []
        for each in operon_list:
            new_list.append(each.strip())
        fp.write(";".join(new_list)+"\n")
    old_fp.close()
    fp.close()
