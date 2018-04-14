import os
import re


def findall_pat(pat, content, result="list"):
    """
    :param result:
    :param pat: string
    :param content: string
    :return: list
    """
    pat = re.compile(pat)
    find = re.findall(pat, content)
    if result == "list":
        return find
    elif result == "one":
        if len(find) > 0:
            return find[0]
        else:
            print("NOT FOUND")
            return find
    else:
        print("usage:\nresult='list'(default)or'one")


def get_strand_dict(gff_file):
    gff_fp = open(gff_file, "r")
    strand_id_dict = {}
    while True:
        line = gff_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        if len(line_content) > 1:
            _id = findall_pat("ID\=([A-Za-z0-9]+)\;", line_content[-1], "one")
            strand_id_dict[_id] = line_content[6]
        else:
            pass
    gff_fp.close()
    return strand_id_dict


def get_annotation(gff_file):
    gff_fp = open(gff_file, "r")
    genes = []
    while True:
        line = gff_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        if len(line_content) > 1:
            start_pos = int(line_content[3])
            stop_pos = int(line_content[4])
            annotation_dict = {}
            annotation_ls = line_content[-1].split(";")
            for ann in annotation_ls:
                split_ann = ann.split("=")
                key = split_ann[0]
                info = split_ann[1].split(",")
                annotation_dict[key] = info
            genes.append([(start_pos, stop_pos), annotation_dict])
        else:
            # print(line)
            pass
    gff_fp.close()
    return genes


def filter_genes(gff_file):
    genes = get_annotation(gff_file)
    i = 0
    curr_len = len(genes)
    tmp_need_del = []
    while i < curr_len:
        annotation = genes[i][1]
        if 'Parent' in annotation:
            # if 'locus_tag' in annotation:
            #     print(genes[i])
            record = i - 1
            gene_id = annotation['Parent']
            while record > 0:
                if genes[record][-1]['ID'] == gene_id:
                    if 'part' not in genes[record][-1]:
                        if genes[record][0] != genes[i][0]:
                            genes[record].insert(-1, genes[i][0])
                            tmp_need_del.append(genes[i])
                            # if 'pseudo' not in genes[record][-1]:
                            #     print(genes[record])  # only 'prfB' without keyword 'pesudo'
                        else:
                            tmp_need_del.append(genes[i])
                        record = 0
                    else:
                        tmp_need_del.append(genes[i])
                        record = 0
                else:
                    record = record - 1
        i = i + 1
    for tmp_del in tmp_need_del:
        genes.remove(tmp_del)
    return genes


def generate_simple_gff(gff_file):
    specie_name = gff_file.split("/")
    specie_name = specie_name[-1]
    tmp_path = os.path.join(specie_name[:-1])
    simple_gff_path = tmp_path + "simple_" + specie_name
    genes = filter_genes(gff_file)
    simple_gff_fp = open(simple_gff_path, 'w')
    for gene in genes:
        if 'locus_tag' not in gene[-1]:
            pass
            # print(gene)  # always with one (start, stop)
            # if 'gbkey' not in gene[-1]:
            #     print(gene)  # NONE
            # start = gene[0][0]
            # stop = gene[0][1]
            # _id = gene[1]['ID'][0]
            # gb_key = gene[1]['gbkey'][0]
            # simple_gff_fp.write("-\t-\t-\t-\t" + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
        else:
            if len(gene) == 2:
                start = gene[0][0]
                stop = gene[0][1]
                _id = gene[1]['ID'][0]
                gb_key = gene[1]['gbkey'][0]
                locus_tag = gene[1]['locus_tag'][0]
                # symbol = gene[1]['gene'][0]
                # synonym = ";".join(gene[1]['gene_synonym'])
                if 'part' in gene[1]:
                    part = gene[1]['part'][0]
                    part_i = part.split("/")[0]
                    # for gene_syn in gene[-1]['gene_synonym']:
                    #     gene_syn = gene_syn + "_" + part_i
                    #     synonym = synonym + ";" + gene_syn
                    # synonym = synonym + ";" + symbol + "_" + part_i
                    simple_gff_fp.write(locus_tag + "\t" + "-" + "\t" + "-" + "\t" + part + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                    simple_gff_fp.write(locus_tag + "\t" + "-" + "\t" + "-" + "\t" + part + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                else:
                    simple_gff_fp.write(locus_tag + "\t" + "-" + "\t" + "-" + "\t" + "-" + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
            else:
                # if 'pseudogene' not in gene[-1]['gene_biotype']:
                #     print(4, gene)  # prfB
                start = gene[0][0]
                stop = gene[0][1]
                _id = gene[-1]['ID'][0]
                gb_key = gene[-1]['gbkey'][0]
                locus_tag = gene[-1]['locus_tag'][0]
                # symbol = gene[-1]['gene'][0]
                # synonym = ";".join(gene[-1]['gene_synonym'])
                simple_gff_fp.write(locus_tag + "\t" + "-" + "\t" + "-" + "\t" + "-" + "\t"
                                    + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                j = 1
                while j < len(gene) - 1:
                    start = gene[j][0]
                    stop = gene[j][1]
                    _id = gene[-1]['ID'][0]
                    gb_key = gene[-1]['gbkey'][0]
                    locus_tag = gene[-1]['locus_tag'][0]
                    # symbol = gene[-1]['gene'][0] + "_" + str(j)
                    # synonym = ";".join(gene[-1]['gene_synonym'])
                    # for gene_syn in gene[-1]['gene_synonym']:
                    #     gene_syn = gene_syn + "_" + str(j)
                    #     synonym = synonym + ";" + gene_syn
                    simple_gff_fp.write(locus_tag + "\t" + "-" + "\t" + "-" + "\t" + "-" + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                    j = j + 1
    simple_gff_fp.close()
    strand_dict = get_strand_dict(gff_file)
    simple_fp = open(simple_gff_path, "r")
    write_fp = open(simple_gff_path + "_2", "w")
    while True:
        line = simple_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        _id = line_content[6]
        if _id in strand_dict:
            write_fp.write(line + "\t" + strand_dict[_id] + "\n")
        else:
            print(_id)
            write_fp.write(line + "\t-\n")
    write_fp.close()
    simple_fp.close()
    os.system("rm -f " + simple_gff_path)
    os.system("mv " + simple_gff_path + "_2 " + simple_gff_path)
    return simple_gff_path


def get_gene_from_file(simple_gff):
    data_list = []
    fp = open(simple_gff, "r")
    while True:
        line = fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        data = {"locus_tag": line_content[0], "start": line_content[4], "stop": line_content[5],
                "strand": line_content[-1]}
        data_list.append(data)
    return data_list


def get_operon_from_file(operon_file):
    data_list = []
    fp = open(operon_file, "r")
    while True:
        line = fp.readline().strip()
        if not line:
            break
        line_content = line.split(";")
        data_list.append(line_content)
    return data_list


if __name__ == '__main__':
    x = [[1, 2], [3, 4], [2, 3]]
    print(sorted(x, key=lambda y: y[0]))
