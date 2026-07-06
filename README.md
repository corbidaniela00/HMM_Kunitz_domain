# Structure-Based HMM for Kunitz-Type Domain Detection

This project addresses the identification of Kunitz-type serine protease inhibitors through a custom-trained HMM built from a structure-guided multiple alignement. 
The full methodology, results, and discussion are described in the report: Kunitz_domain_HMM.pdf.

## Project overview

The Kunitz-type domain is a highly conserved $\alpha+\beta$ structural motif crucial for regulating serine protease activity. 
Due to deep evolutionary divergence, its primary sequence often falls into the "twilight zone" of sequence identity, making traditional sequence-based tools like BLAST less effective for remote homology detection.
To overcome this limitation was developed a computational pipeline that builds a profile HMM directly from a multiple structure alignment of experimentally solved Kunitz-domain structures, rather than from a standard sequence alignment, and validates it against a large, curated Swiss-Prot dataset.

## Repository Structure

```yaml
.
├── data/
    #used as input for filter_PDB_sequences.py
│   ├── rcsb_pdb_custom_report.json 
│   ├── dataset_pulito.csv
    #used as input for MMSEQ
│   ├── sequences_for_clustering.fasta
    #output of MMSSEQ
│   ├── mmseqs2_2915909.txt
│   ├── clusters_con_info.txt
│   ├── seed_alignment_input.fasta
#used as input for download_structures_for_MSA.py
│   ├── lista_pdb.txt
# the following three files are used as input of mTM-align (the last 2 for the analisys of FP and FN)
|   ├── lista_PDB_chain.txt
|   ├── PDB_chain_False_Negatives.txt
|   ├── PDB_chain_False_Positive.txt
│   ├── cross_validation/
|   |   ├── Kunitz_set_1.txt
|   |   ├── Kunitz_set_2.txt
│   └── processed/
├── models/
│   └── Kunitz_HMM.hmm
├── scripts/
│   ├── filter_PDB_sequences.py
|   ├── update_with_resolution_MMSEQ.py
|   ├── select_one_seq_per_cluster.py
|   ├── download_structures_for_MSA.py
|   ├── compute_performances.py
│   └── performance_analysis.py
├── README.md
└── requirements.txt
```
## Project workflow

### 1. High-quality Kunitz structures were retrieved from RCSB PDB and filtered using MMseqs2 to remove redundancy. 
* Uniprot filters (**python code:**`filter_PDB_sequences.py` **output:**`dataset_pulito.csv`, `sequences_for_clustering.fasta`)
  * Pfam ID: PF00014
  * Resolution ≤ 3 Å
  * Sequence length between 40–70 residues
        
* MMSEQ filters (**python code:**`update_with_resolution_MMSEQ.py`, `select_one_seq_per_cluster.py` **output:**`clusters_con_info.txt`, `seed_alignemet_input.fasta`)
  - sequence identity: 0.95
  - coverage: 0.85
          
### 2. Non-redundant domains were then aligned spatially via mTM-align to capture structural conservation independent of sequence identity. 
* it's necessary to download the sofware (yanglab.qd.sdu.edu.cn/mTM-align) in order to perform the alignement via: `./mTM-align -i lista_pdb.txt -o alignment_output`
*  manual refinement of alignement to reduce residual redundancy, yielding a final set of 18 structures

### 3. Structure-derived alignment used to train a custom Profile Hidden Markov Model (HMMER3), subsequently vaidated against Swiss-Prot database. 
after creating a CONDA environment with `hmmer` installed and having downloaded from SwissProt respectively the proteins with/without the kunitz domain ( that I'm goint to use to validate my model) I proceed with the following commands

- I start building the HMM model, based on the structure alignement downloades from FoldSeek `hmmbuild name_model.hmm alignment_fasta.fa`
- `zcat uniprotkb_reviewed_true_AND_xref_pfam_P_2026_04_24.fasta.gz > positive_kunitz.fasta`
- `zcat uniprotkb_reviewed_true_NOT_xref_pfam_P_2026_04_24.fasta.gz > negative_kunitz.fasta`
- `hmmsearch --noali --max --tblout positive_kunitz.search -Z 1000 Kunitz_model.hmm positive_kunitz.fasta`
- `hmmsearch --noali --max --tblout negative_kunitz.search -Z 1000 Kunitz_model.hmm negative_kunitz.fasta`

- **Formatting the positive set** (ID, best-domain E-value, label 1), split evenly across the two folds: 

  - `grep -v '^#' positive_kunitz.search |awk '{print $1"\t"$8"\t1"}'| sort -R > positive_kuniz.match`
  - `head -n 195 positive_kunitz.match > kunitz_set_1.txt`
  - `tail -n 195 positive_kunitz.match > kunitz_set_2.txt`
  
- **Formatting the negative set** (ID, best-domain E-value, label 0; non-matching sequences are assigned a default E-value of 10 so they are still included as true negatives)

  - `grep -v '^#' negative_kunitz.search |awk '{print $1"\t"$8"\t0"}' > negative_kuniz.match`
  - `grep ">" negative_kunitz.fasta | awk '{print $1 }'| tr -d ">"|sort > negative_kunitz.ids`
  - `awk '{print $1 }' negative_kunitz.match|sort > negative_kunitz_match.ids`
  - `comm -23 negative_kunitz.ids negative_kunitz_match.ids | awk '{ print $1"\t"10"\t"0 }' > negative_kunitz.nomatch`
  - `cat negative_kunitz.match negative_kunitz.nomatch |sort -R > negative_kunitz_tot.txt`
  - `head -n 287115 negative_kunitz_tot.txt >> kunitz_set_1.txt`
  - `tail -n 287114 negative_kunitz_tot.txt >> kunitz_set_2.txt`

### 4. Performances and error analysis
Performance was computed with compute_performances.py (confusion matrices, MCC vs. E-value threshold) and performance_analisys.py (ROC curves, AUC), following standard 2-fold cross-validation: the threshold maximizing the Matthews Correlation Coefficient (MCC) on each training fold was applied to the corresponding held-out test fold.

Key results (see report for full details):
- MCC ≥ 0.99 and AUC = 1.0000 on both folds, stable across a broad E-value threshold range (10⁻⁴ to 10⁻⁸)
- Only 4 false negatives and 3 false positives across the entire validation set (574,619 sequences)

Misclassified sequences were further examined via multiple structure alignment (mTM-align) against a canonical Kunitz reference structure (1AAP_A), to determine whether they represent genuine structural homologs missed at the sequence level, or non-domain artifacts:
- False negatives are structurally confirmed Kunitz domains (TM-score = 0.600) missed due to sequence-level divergence beyond the profile's sensitivity.
- False positives are short, likely truncated fragments (TM-score = 0.355) that match only a single conserved cysteine motif, without the complete Kunitz fold.

##  Requirements
- HMMER3 (hmmbuild, hmmsearch)
- mTM-align for multiple structure alignment
- MMseqs2 for sequence clustering
- AliView for alignment visualization/manual curation
- Python 3.x with numpy, matplotlib, seaborn, scikit-learn
