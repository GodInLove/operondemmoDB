import os

from PyOpdb.network.ncbi import get_paired_or_singled
from PyOpdb.operon_predict.download_fastq import srr_n_to_fastq
from PyOpdb.operon_predict.download_fna_gff import download_annotation
from PyOpdb.operon_predict.pipline import extract_Synonym, get_operon
from app import path, sender, self_link, mail, app
from app.model import SrrTask, TaskId
from multiprocessing import Pool
from app import process
from datetime import datetime
from flask_mail import Message


def operon_predict(srr_list, kegg_id, soft, method, corr, srr_id):
    if len(srr_list) == 1:
        soft = "rockhopper"
    all_srr_list = []
    paired_or_not_list = []
    download_path_list = []
    i_iter = 0
    for con in srr_list:
        condition_path = os.path.join(path, srr_id, "fastq", "c" + str(i_iter))
        if not os.path.exists(condition_path):
            os.makedirs(condition_path)
        for rep in con:
            tmp_ = get_paired_or_singled(rep)
            if tmp_ == 0:
                soft = "rockhopper"
            paired_or_not_list.append(tmp_)
            all_srr_list.append(rep)
            download_path_list.append(condition_path)
        i_iter = i_iter + 1

    pool = Pool(process)
    _list = pool.starmap(srr_n_to_fastq, zip(all_srr_list, paired_or_not_list, download_path_list))
    pool.close()
    pool.join()
    kegg_path = download_annotation(kegg_id, path)
    browse_link = "http://" + "127.0.0.1" + "/JBrowse/?data=" + srr_id
    if soft == "rockhopper":
        condition_str = get_condition_str_rockhopper(download_path_list, paired_or_not_list, all_srr_list)
        rockhopper_path = os.path.join(path, "tools", "Rockhopper.jar")
        out_path = os.path.join(path, srr_id, "operon")
        os.system("java -Xmx3g -cp " + rockhopper_path + " Rockhopper -p " + str(process) + " -g " + kegg_path + " " +
                  condition_str + " -o " + out_path)
        extract_Synonym(kegg_path, out_path)
        get_operon(out_path)
        new_srr_task = SrrTask(_id=srr_id, kegg_id=kegg_id, operon_path="/instance/" + srr_id +
                               "/operon/operon.txt", method="rockhopper",
                               add_time=datetime.now(), bw_path="/instance/" + srr_id +
                               "/operon/operon.txt", browse_link=browse_link)
        new_srr_task.get_srr_nums(srr_list)
        new_srr_task.get_operons_from_file(os.path.join(out_path, "operon.txt"))
        new_srr_task.save()
        res2jbrowse(kegg_path, out_path, srr_id)
    else:
        input_path = os.path.join(path, "fastq")
        fna_path = os.path.join(kegg_path, kegg_id + ".fna")
        gff_path = os.path.join(kegg_path, kegg_id + ".gff")
        out_path = os.path.join(path, srr_id, "operon")
        print(input_path,fna_path,gff_path,out_path)
        if corr == "c_i_j":
            os.system("operondemmo -i " + input_path + " -g " + gff_path + " -f " + fna_path
                      + " -m " + method + " -p " + str(process) + " -t 0.6 " + " -o " + out_path)
        elif corr == "spearman":
            os.system("operondemmo -i " + input_path + " -g " + gff_path + " -f " + fna_path
                      + " -m " + method + " -p " + str(process) + " -t 0.6 " + " -o " + out_path + " --spearman")
        else:
            os.system("operondemmo -i " + input_path + " -g " + gff_path + " -f " + fna_path
                      + " -m " + method + " -p " + str(process) + " -t 0.6 " + " -o " + out_path + " --person")
        new_srr_task = SrrTask(_id=srr_id, kegg_id=kegg_id, operon_path="/instance/" + srr_id +
                               "/operon/operon.txt", method=method,
                               add_time=datetime.now(), bw_path="/instance/" + srr_id +
                               "/operon/operon.txt", browse_link=browse_link)
        new_srr_task.get_srr_nums(srr_list)
        new_srr_task.get_operons_from_file(os.path.join(out_path, "operon.txt"))
        new_srr_task.save()
        res2jbrowse(kegg_path, out_path, srr_id)
    task_query = TaskId.objects.get_or_404(srr_id=srr_id)
    msg = Message("OperondemmoDB Task", sender=sender, recipients=[task_query.email])
    msg.body = "your task link: " + self_link + "/task/" + task_query.task_id
    send_async_email(app, msg)
    print("send it OK")


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def get_condition_str_rockhopper(download_path_list, paired_or_not_list, all_srr_list):
    record_condition = ""
    condition_list = []
    i_iter = 0
    while i_iter < len(all_srr_list):
        condition = download_path_list[i_iter].split("/")[-1]
        if condition != record_condition:
            condition_list.append([])
            record_condition = condition
        if paired_or_not_list[i_iter] == 1:
            condition_list[-1].append(download_path_list[i_iter] + "/" + all_srr_list[i_iter] + "_1.fastq.gz%"
                                      + download_path_list[i_iter] + "/" + all_srr_list[i_iter] + "_2.fastq.gz")
        else:
            condition_list[-1].append(download_path_list[i_iter] + "/" + all_srr_list[i_iter] + ".fastq.gz")
        i_iter = i_iter + 1
    new_condition_list = []
    for con in condition_list:
        new_condition_list.append(",".join(con))
    condition_str = " ".join(new_condition_list)
    return condition_str


def res2jbrowse(ref_path, result_path, srr_n):
    j_path = "/var/www/html/JBrowse"
    if not os.path.exists(os.path.join(j_path, srr_n)):
        # the path of Jbrowse
        # handle reference sequence .fasta
        os.system("cd " + j_path + " && bin/prepare-refseqs.pl --fasta " + ref_path + "/*.fna")
        # handle reference .gff
        os.system(
            "cd " + j_path + " && bin/flatfile-to-json.pl --gff " + ref_path + "/*.gff --trackType CanvasFeatures --trackLabel gff")
        # names
        # move rockhopper result
        os.system("cp " + result_path + "/*txt " + j_path + "/data/")
        os.system("mv " + j_path + "/data/tracks.conf " + j_path + "/data/tracks.cofn")
        # change name "data" to srr_n
        os.system("cd " + j_path + " && bin/generate-names.pl -v")
        os.system("cd " + j_path + " && mv data " + srr_n)


if __name__ == '__main__':
    operon_predict([['SRR3344818'], ['SRR3344819']], "eco", "operondemmo", "GD", "c_i_j", "SRR3344818-SRR3344819")
