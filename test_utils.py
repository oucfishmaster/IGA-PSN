import os
import torch
import torchvision.utils as vutils
import numpy as np
from models import model_utils
from utils import eval_utils, time_utils

import torch.nn.functional as F

def get_itervals(args, split):
    args_var = vars(args)
    disp_intv = args_var[split + '_disp']
    save_intv = args_var[split + '_save']
    return disp_intv, save_intv

def test(args, split, loader, model, log, epoch, recorder):
    model.eval()
    print('---- Start %s Epoch %d: %d batches ----' % (split, epoch, len(loader)))
    timer = time_utils.Timer(args.time_sync);

    disp_intv, save_intv = get_itervals(args, split)
    with torch.no_grad():
        for i, sample in enumerate(loader):
            data = model_utils.parseData(args, sample, timer, split)
            input = model_utils.getInput(args, data)
            _, _, out_var3 = model(input)
            timer.updateTime('Forward')
            acc, error_map = eval_utils.calNormalAcc(data['tar'].data, out_var3.data, data['m'].data)
            recorder.updateIter(split, acc.keys(), acc.values())
            iters = i + 1
            if iters % disp_intv == 0:
                opt = {'split': split, 'epoch': epoch, 'iters': iters, 'batch': len(loader),
                       'timer': timer, 'recorder': recorder}
                log.printItersSummary(opt)

            if iters % save_intv == 0:
                pred = (out_var3.data + 1) / 2
                masked_pred = pred * data['m'].data.expand_as(out_var3.data)
                log.saveNormalResults(masked_pred, split, epoch, iters)
                log.saveErrorMap(error_map, split, epoch, iters)      

    opt = {'split': split, 'epoch': epoch, 'recorder': recorder}
    log.printEpochSummary(opt)
