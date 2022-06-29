#!/usr/bin/env python
import sys, os, os.path
import numpy as np
import json
from sklearn.metrics import roc_auc_score

def dcg_score(y_true, y_score, k=10):
    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])
    gains = 2 ** y_true - 1
    discounts = np.log2(np.arange(len(y_true)) + 2)
    return np.sum(gains / discounts)


def ndcg_score(y_true, y_score, k=10):
    best = dcg_score(y_true, y_true, k)
    actual = dcg_score(y_true, y_score, k)
    return actual / best


def mrr_score(y_true, y_score):
    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order)
    rr_score = y_true / (np.arange(len(y_true)) + 1)
    return np.sum(rr_score) / np.sum(y_true)

def parse_line(l):
    impid, ranks = l.strip('\n').split()
    ranks = json.loads(ranks)
    return impid, ranks

def scoring(truth_f, sub_f):
    aucs = []
    mrrs = []
    ndcg5s = []
    ndcg10s = []
    
    line_index = 1
    for lt in truth_f:
        ls = sub_f.readline()
        impid, labels = parse_line(lt)
        
        if labels == []:
            continue 
        
        if ls == '':
            sub_impid = impid
            sub_ranks = [1] * len(labels)
        else:
            sub_impid, sub_ranks = parse_line(ls)

        
        lt_len = float(len(labels))
        
        y_true = np.array(labels,dtype='float32')
        y_score = []
        for rank in sub_ranks:
            score_rslt = 1./rank
            if score_rslt < 0 or score_rslt > 1:
                raise ValueError("Line-{}: score_rslt should be int from 0 to {}".format(line_index,lt_len))
            y_score.append(score_rslt)
            
        auc = roc_auc_score(y_true,y_score)
        mrr = mrr_score(y_true,y_score)
        ndcg5 = ndcg_score(y_true,y_score,5)
        ndcg10 = ndcg_score(y_true,y_score,10)
        
        aucs.append(auc)
        mrrs.append(mrr)
        ndcg5s.append(ndcg5)
        ndcg10s.append(ndcg10)
        
        line_index += 1

    return np.mean(aucs), np.mean(mrrs), np.mean(ndcg5s), np.mean(ndcg10s)
        

if __name__ == '__main__':
    output_filename = '/Users/wangshicheng/PycharmProjects/news_recommendation/Method_GPU/evaluate_result/scores.txt'
    output_file = open(output_filename, 'w')

    truth_file = open('/Users/wangshicheng/PycharmProjects/news_recommendation/Method_GPU/evaluate_result/truth.txt', 'r')
    predict_file = open('/Users/wangshicheng/PycharmProjects/news_recommendation/Method_GPU/evaluate_result/prediction.txt', 'r')

    auc, mrr, ndcg, ndcg10 = scoring(truth_file, predict_file)

    output_file.write("AUC:{:.4f}\nMRR:{:.4f}\nnDCG@5:{:.4f}\nnDCG@10:{:.4f}".format(auc, mrr, ndcg, ndcg10))
    output_file.close()