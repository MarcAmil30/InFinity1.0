#!/bin/bash
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=1:mem=10gb
#PBS -N mutate_permutations_array
#PBS -J 1-20 

module load anaconda3/personal 
source activate pipeline_env

cd $PBS_O_WORKDIR
python3 modified_permutation.py $limit_r 


