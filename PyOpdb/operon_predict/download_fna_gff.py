import os
import re
import urllib.request
from PyOpdb.scripts import connect_url, callback


def download_annotation(kegg_id, _path):
    """
    :method: a method to download annotion files like .fna .gff and .ptt .rnt
    :param kegg_id: string like "eco"
    :param anno_path:
    :return: void(some files in anno_path)
    """
    print("\ndownloading annotion:.gtf .rnt .gff.......\n")
    download_path = os.path.join(_path, kegg_id)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    # check whether the anno_path exists or not
    # get the ncbi ftp url through the kegg organisms website
    kegg_url = "http://www.genome.jp/kegg-bin/show_organism?org="
    print("search in the kegg database\n")
    url = kegg_url + kegg_id
    html = connect_url(url, decode='utf-8')
    url_download = get_url(html)
    # downloading fna and gff and convert gff to ptt/rnt
    print("downloading fna....")
    if not os.path.exists(os.path.join(download_path, kegg_id+'.fna')):
        # download url
        url_fna = url_download + "_genomic.fna.gz"
        # download path
        local_fna = os.path.join(download_path, kegg_id + ".fna.gz")
        # download method
        urllib.request.urlretrieve(url_fna, local_fna, callback)
        os.system("gzip -d " + local_fna)
        os.system("rm " + local_fna)
    print("downloading gff....")
    if not os.path.exists(os.path.join(download_path, kegg_id+".gff")):
        url_gff = url_download + "_genomic.gff.gz"
        local_gff = os.path.join(download_path, kegg_id + ".gff.gz")
        urllib.request.urlretrieve(url_gff, local_gff, callback)
        os.system("gzip -d " + local_gff)
        os.system("rm " + local_gff)
    print("downloading feature_table....")
    if not os.path.exists(os.path.join(download_path, kegg_id+".ptt")):
        url_feature = url_download + "_feature_table.txt.gz"
        local_feature = os.path.join(download_path, kegg_id + "_feature.txt.gz")
        urllib.request.urlretrieve(url_feature, local_feature, callback)
        os.system("gzip -d " + local_feature)
        new_path = os.path.join(download_path, kegg_id + "_feature.txt")
        generate_ptt_rnt(new_path, download_path, kegg_id)
        os.system("rm " + new_path)
        os.system("rm " + local_feature)
    print("keggID:" + kegg_id + " , its annotion files were downloaded in the " + download_path)
    return download_path


def get_url(content):
    """
    :method: a sub-method to get the refSeq or GenBank ftp url of a specie through kegg id
    :param content: string
    :return: string
    """
    pat = re.compile("(ftp\:\/\/ftp\.ncbi\.nlm\.nih\.gov\/[a-z\/A-Z0-9\_\.]+)")
    result = re.findall(pat, content)
    name = result[0].split("/")[-1]
    url_download = result[0] + "/" + name
    return url_download


def generate_ptt_rnt(feature_file, path, kegg_id):
    fp = open(feature_file, "r")
    ptt_path = os.path.join(path, kegg_id + ".ptt")
    ptt_fp = open(ptt_path, "w")
    ptt_fp.write("Location\tStrand\tLength\tPID\tGene\tSynonym\tCode\tCOG\tProduct\n")
    rnt_path = os.path.join(path, kegg_id + ".rnt")
    rnt_fp = open(rnt_path, "w")
    rnt_fp.write("Location\tStrand\tLength\tPID\tGene\tSynonym\tCode\tCOG\tProduct\n")
    while True:
        line = fp.readline().strip()
        if not line:
            break
        if "#" in line:
            pass
        else:
            line2 = fp.readline().strip()
            line_content = line.split("\t")
            line_content2 = line2.split("\t")
            location = line_content[7] + ".." + line_content[8]
            strand = line_content[9]
            length = line_content2[-1]
            gene = line_content[14]
            locus_tag = line_content[16]
            if line_content[1] == "protein_coding":
                ptt_fp.write(
                    location + "\t" + strand + "\t" + length + "\t" + "-" + "\t" + gene + "\t" + locus_tag
                    + "\t" + "-" + "\t" + "-" + "\t-\n")
            else:
                rnt_fp.write(
                    location + "\t" + strand + "\t" + length + "\t" + "-" + "\t" + gene + "\t" + locus_tag
                    + "\t" + "-" + "\t" + "-" + "\t-\n")
    fp.close()
    ptt_fp.close()
    rnt_fp.close()
