# InFinity 1.0
This is the offical page for the InFinity 1.0 ligand-affinity centered protein re-engineering pipeline, as developed by the  Imperial College London team for the 2022 iGEM competition. 

## Description
InFinity 1.0 is protein reengineering framework which utilises five _in silico_ steps to perform high-throughput mutagenesis, screening of sampled mutants affinity to a chosen ligand, followed by ranking and multiple sequence allignment to identify potential motifs that can alter ligand specificity/affinity. What makes this tool novel is the implementation of several highly efficient recently released tools in a plug-and-play framework, improving accesibility. With the exception of the first step, each of the steps in the current framework utilise published or pre-published open-source tools, and as such acknowledgments should go to the respective authors. Initial testing has shown similar scoring power to established scoring functions, yet we aknowledge that further improvments are necessitated, especially in terms of energy minimisation and fold prediction following mutagensis, if we are to consider directly screening top mutants generated from this pipeline. Nonetheless, in its current state InFinity 1.0 serves as an extra tool in the toolkit of a synthetic biologist, to help aid in rational design and potentially  help narrow down screening efforts. 

To use the framework the user should have access to a computing cluster with GPU-capability along with 1tb of storage per 1,000,000 mutants to be screened.
The current release is made for PBS-type HPC schedulers, but it may easily be addapted for SLURM schedulers aswell. 
## Instalation
First clone InFinity to a directory within the computing cluster. Next install MGLTools if this is not already on your system (MGLTools can be downloaded from https://ccsb.scripps.edu/mgltools/downloads/). MSMS can then be downloaded from https://ccsb.scripps.edu/msms/downloads/ and installed as such: 
```
cd [USER_DIR]/delta_LinF9_XGB/software/
mkdir msms
tar -zxvf msms_i86_64Linux2_2.6.1.tar.gz -C msms
cd msms
cp msms.x86_64Linux2.2.6.1 msms
```
Next install AlphaSpace2 as such:
```
cd [USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/software/
tar -zxvf AlphaSpace2_2021.tar.gz
cd AlphaSpace2_2021
pip install -e ./
```
With this done, it's time to ensure the pipline knows what and where to run. Therefore, perform the following edits:
Edit ``InFinity/Docking/EquiBind/configs_clean/inference.yml``, substituting [USER_DIR] in the highlighted filepaths for the filepath of InFInity in your cluster. 
Simmilarly the following files should be edited, replacing [USER_DIR]:
``InFinity/Scoring/Delta_LinF9_XGB/script/runXGB.py``<br>
``InFinity/Scoring/Delta_LinF9_XGB/script/calc_vina_features.py``<br>
``InFinity/Scoring/Delta_LinF9_XGB/script/prepare_betaAtoms.py``<br>
``InFinity/Scoring/Delta_LinF9_XGB/software/msms/pdb_to_xyzr``<br>
``InFinity/Scoring/Delta_LinF9_XGB/script/calc_bridge_wat.py``<br>
``InFinity/Scoring/Delta_LinF9_XGB/script/featureSASA.py``<br>

The final installation step is to get the conda modules in order. For compatability reasons we advice you use python 3.7.
Navigate to InFinity and install the two conda environments from the supplied environment.yml file thorugh ``conda env create -f environment_docking.yml`` and ``conda env create -f environment_scoring.yml``.

## Usage
**Step 1: combinatorial mutagenesis**

1. First navigate to the input_trial.csv file in the main folder. Insert the sequence of the protein in ``SEQUENCE`` column, and the positions whished to be mutated in the ``POSITION TO MUTATE``column, seperating each with a comma.

2. Navigate to the InFinity directory and edit the mutate.sh array job argument e.g. ``#PBS -J 0-19`` according to the computational resources available

3. Run combinatorial and structural mutagenesis:

    ```
    qsub -v limit="1000000" mutate.sh
    ```

**Step 2: Structural Mutagenesis**
4. In the framework's current implementation, structural mutagenesis is done immediately after combinatorial mutagenesis, as part of the same script. This step has been left included to allow for future improvments, where splitting up the two jobs is more appropriate. 

**Step 3: Docking**

5. Navigate to InFinity/Docking/EquiBind and run:
    ```
    qsub -v file_dir="[USER_DIR]/InFinity/Docking/EquiBind" runeq.sh
    ```
**Step 4: Scoring**

6. Navigate to InFinity/Docking/Delta_LinF9_XGB and run:

    ```
    qsub -v file_dir="[USER_DIR]/InFinity" move.sh
    ```

7. Edit the ``#PBS -J 0-99`` argument of ``scoring.sh`` according to the computational resources avaliable.


8. Perform docking by running: 

    ```
    qsub -v processors="100" scoring.sh
    ```
    Edit processors to suit the configuration 
9. The previous step will generate n score.csv files where n is the number of processors used to run the step. These can be concatnated ``cat scores*.csv > final_scores.csv`` These can then be ranked with ``sort -k2 -n -t, final_scores.csv``

**Step 5: Multiple Sequence Allignment**
10. Using the scores generated from the previous step, mutants with a desired alteration in ligand affinity/specificity can then be uploaded and screened using an MSA tool such as Clustal Omega, with enriched motifs serving as strarting point for further rational design/ screening analysis 

## Contributions
With the interchangability of the invidual steps, we encourage community contributions to test out other tools and help us continously improve the framework.

## Authors and acknowledgment
The framework was developed by Marc Amil and Rasmus Hildebrandt.
With the exception of the tool performing combinatorial mutagenesis remaining steps heavily relief on the adaptation of several published tools were used and sduch we thank the authors for making their work freely available:

Liu, Zhihai; Su, Minyi; Han, Li; Liu, Jie; Yang, Qifan; Li, Yan; Wang, Renxiao., 2017, ‘Forging the Basis for Developing Protein-Ligand Interaction Scoring Functions’, Accounts of Chemical Research, 50 (2): pp. 302-309. Available at: http://www.pdbbind.org.cn/index.php

Schrödinger, L. & DeLano, W., 2020. PyMOL, Available at: http://www.pymol.org/pymol.

Stärk, H. et al., 2022, ‘EquiBind: Geometric Deep Learning for Drug Binding Structure Prediction’. Available at: https://doi.org/10.48550/arXiv.2202.05146.

Yang, C. and Zhang, Y., 2022, ‘Delta Machine Learning to Improve Scoring-Ranking-Screening Performances of Protein–Ligand Scoring Functions’, Journal of Chemical Information and Modeling, 62(11), pp. 2696–2712. Available at: https://doi.org/10.1021/acs.jcim.2c00485.


