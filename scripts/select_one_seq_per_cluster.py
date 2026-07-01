import pandas as pd

csv_input =  r'C:\Users\Daniela\Desktop\Bioinformatics\Laboratory of Bioinformatics 1\MODULO 2\progetto\dataset_pulito.csv'
cluster_input =  r'C:\Users\Daniela\Desktop\Bioinformatics\Laboratory of Bioinformatics 1\MODULO 2\progetto\clusters_con_info.txt'
output_fasta =  r'C:\Users\Daniela\Desktop\Bioinformatics\Laboratory of Bioinformatics 1\MODULO 2\progetto\seed_alignment_input.fasta'


clusters = {}
current_cluster = None

with open(cluster_input, 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue # Salta righe vuote

        if line.startswith("Cluster#"):
            current_cluster = line.split('#')[1].strip()
            current_best_res = 999.0
            clusters[current_cluster] = []

        elif line.startswith(">"):
           # Dividiamo la riga per spazi
            # Esempio: >3WNY_I RPAFCLE... 1.3
            parts = line.split()
            header = parts[0]      # >3WNY_I
            sequence = parts[1]    # RPAFCLE...
            res_value = float(parts[2]) # 1.3
            
            # Se questa risoluzione è migliore (minore) della precedente nel cluster
            if res_value < current_best_res:
                current_best_res = res_value
                current_best_entry = (header, sequence)
                clusters[current_cluster] = current_best_entry



with open(output_fasta, 'w') as f:
    for c_id in clusters:
        vincitore = clusters[c_id]
        if vincitore: # Controlliamo che il cluster non sia rimasto vuoto
            header, seq = vincitore
            f.write(f"{header}\n{seq}\n")

print(f" Selezionati {len(clusters)} rappresentanti (uno per cluster).")
