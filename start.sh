#!/bin/bash

#启用虚拟环境
eval "$(conda shell.bash hook)"
conda activate LHM

#关闭占用7860端口进程
process=`lsof -t -i:7860`
if [ "${process}" != "" ]; then
    kill -9 ${process}
fi

rm nohup.out 2>/dev/null
rm nohup.log 2>/dev/null

nohup python -u ./app.py 1>nohup.out 2>nohup.log &

