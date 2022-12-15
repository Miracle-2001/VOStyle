import importlib
from networks.engine.eval_manager import Evaluator
import sys
sys.path.append('.')
sys.path.append('..')

global_atrous_rate = 2
pretrain_model_path = "./pretrain_models/resnet101_cfbi.pth"
dataset_name = "myVideo"
using_float16 = True
gpu_id = 0


def load_configs():
    import argparse
    parser = argparse.ArgumentParser(description="Eval CFBI")
    parser.add_argument('--exp_name', type=str, default='')

    parser.add_argument('--config', type=str, default='configs.resnet101_cfbi')

    parser.add_argument('--gpu_id', type=int, default=0)
    parser.add_argument('--ckpt_path', type=str, default='')
    parser.add_argument('--ckpt_step', type=int, default=-1)

    parser.add_argument('--dataset', type=str, default='')

    parser.add_argument('--flip', action='store_true')
    parser.set_defaults(flip=False)
    parser.add_argument('--ms', nargs='+', type=float, default=[1.])
    parser.add_argument('--max_long_edge', type=int, default=-1)

    parser.add_argument('--float16', action='store_true')
    parser.set_defaults(float16=True)
    parser.add_argument('--global_atrous_rate', type=int, default=1)
    parser.add_argument('--global_chunks', type=int, default=4)
    parser.add_argument('--min_matching_pixels', type=int, default=0)
    parser.add_argument('--no_local_parallel',
                        dest='local_parallel', action='store_false')
    parser.set_defaults(local_parallel=True)
    args = parser.parse_args()

    config = importlib.import_module(args.config)
    cfg = config.cfg

    cfg.TEST_GPU_ID = gpu_id

    if args.exp_name != '':
        cfg.EXP_NAME = args.exp_name

    cfg.TEST_CKPT_PATH = pretrain_model_path

    if args.ckpt_step > 0:
        cfg.TEST_CKPT_STEP = args.ckpt_step

    cfg.TEST_DATASET = dataset_name

    cfg.TEST_FLIP = args.flip
    cfg.TEST_MULTISCALE = args.ms
    if args.max_long_edge > 0:
        cfg.TEST_MAX_SIZE = args.max_long_edge
    else:
        cfg.TEST_MAX_SIZE = 800 * 1.3 if cfg.TEST_MULTISCALE == [1.] else 800

    cfg.MODEL_FLOAT16_MATCHING = using_float16

    if 'cfbip' in cfg.MODEL_MODULE:
        cfg.TEST_GLOBAL_ATROUS_RATE = [global_atrous_rate, 1, 1]
    else:
        cfg.TEST_GLOBAL_ATROUS_RATE = global_atrous_rate

    cfg.TEST_GLOBAL_CHUNKS = args.global_chunks
    cfg.TEST_LOCAL_PARALLEL = args.local_parallel

    if args.min_matching_pixels > 0:
        cfg.TEST_GLOBAL_MATCHING_MIN_PIXEL = args.min_matching_pixels

    return cfg


def prediction(congfig):
    evaluator = Evaluator(cfg=congfig)
    evaluator.evaluating()


if __name__ == "__main__":

#def start_prediction():
    cfg = load_configs()
    # 把mask和帧都生成，并且放入相应文件。
    # 再生成一个json，放入固定位置
    prediction(cfg)
