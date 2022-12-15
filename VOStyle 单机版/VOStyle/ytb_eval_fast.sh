config="configs.resnet101_cfbi"
datasets="myVideo"
ckpt_path="./pretrain_models/resnet101_cfbi.pth"
python tools/eval_net.py --config ${config} --dataset ${datasets} --ckpt_path ${ckpt_path}  --float16 --global_atrous_rate 2
