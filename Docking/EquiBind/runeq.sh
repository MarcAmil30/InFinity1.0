#!/bin/bash
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=4:mem=24gb:ngpus=1
#PBS -N Equibind_Docking
cd $file_dir
module load anaconda3/personal
source activate equibind
python inference.py --config=$file_dir/configs_clean/inference.yml
