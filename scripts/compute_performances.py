
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay #per visualizzare la confucion matrix come immagine

from pathlib import Path

current_file_path = Path(__file__).resolve() 
output_dir = current_file_path.parent / "output_figures"
output_dir.mkdir(parents=True, exist_ok=True)

#--------------------------------------------------Funcion Definition------------------------------------------------ 

def get_predictions(file):
    preds = []
    
    with open(file) as fh:
        for line in fh:
            v = line.rstrip().split()
            if len(v) < 3: continue
            # v[0]=ID, v[1]=E-value, v[2]=Class (0 o 1)
            
            preds.append((v[0], float(v[1]), int(v[2])))
    return preds #returns a list of tuples

def get_confusion_matrix(preds, threshold=0.001):
    # Matrice: Righe = Classe Reale (0,1), Colonne = Predizione (0,1)
    cm = np.zeros((2, 2))
    for p in preds:
        real_class = p[2]
        # Predizione: 1 se E-value <= soglia, 0 altrimenti
        if p[1] <= threshold:
            pred_class = 1 
        else:  pred_class =0
        cm[real_class, pred_class] += 1
    return cm

def get_metrics(preds, threshold): #ritorna accuracy e mcc
    cm = get_confusion_matrix(preds, threshold)
    tp, tn, fn, fp = cm[1,1], cm[0,0], cm[1,0], cm[0,1]
    
    q2 = (tp + tn) / np.sum(cm) if np.sum(cm) > 0 else 0 #q2 corrisponde all'accuracy
    
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = (tp * tn - fp * fn) / np.sqrt(denom) if denom > 0 else 0 #mattew correlation coefficient
    
    return q2, mcc

def save_confusion_matrix(cm, filename, title):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='.0f', cmap='coolwarm', 
                xticklabels=['Pred 0', 'Pred 1'], 
                yticklabels=['Real 0', 'Real 1'])
    plt.title(title)
    plt.ylabel('Classe Reale')
    plt.xlabel('Classe Predetta')
    plt.savefig(output_dir/filename)
    plt.close()
    print(f"Salvata: {filename}")
'''
def cross_validate(train_preds, test_preds, label):
    thresholds = [10**-i for i in range(1, 16)]
    best_mcc = -1
    best_th = 0
    
    # 1. Trova la best threshold sul set di training
    for th in thresholds:
        _, mcc = get_metrics(train_preds, th)
        if mcc > best_mcc:
            best_mcc = mcc
            best_th = th
            
    # 2. Calcola la CM sul set di test usando la best_th trovata
    final_cm = get_confusion_matrix(test_preds, best_th)
    
    # 3. Salva il grafico
    save_confusion_matrix(final_cm, f'cm_{label}.png', f'Confusion Matrix - {label} (Best Th: {best_th:.1e})')
    
    return best_th, final_cm
'''
def find_best_threshold(train_preds, thresholds):
    best_mcc, best_th = -1, None
    for th in thresholds:
        _, mcc = get_metrics(train_preds, th)
        if mcc > best_mcc:
            best_mcc, best_th = mcc, th
    return best_th

def cross_validate(train_preds, test_preds, label, thresholds):
    best_th = find_best_threshold(train_preds, thresholds)
    final_cm = get_confusion_matrix(test_preds, best_th)#Calcola la CM sul set di test usando la best_th trovata
    save_confusion_matrix(final_cm, f'cm_{label}.png', f'Confusion Matrix - {label} (Best Th: {best_th:.1e})')  # I/O separato
    return best_th, final_cm

def get_errors(preds, threshold):
    false_positives=[]
    false_negatives=[]
    for p in preds:
        real_class = p[2]
        pred_class = 1 if p[1] <= threshold else 0
        if real_class==0 and pred_class==1:
            false_positives.append((p[0],p[1]))
        if real_class==1 and pred_class==0:
            false_negatives.append((p[0], p[1]))

    return false_positives, false_negatives

if __name__ == '__main__':
    
    file1 =current_file_path.parent/'kunitz_set_1.txt'
    file2 =current_file_path.parent/'kunitz_set_2.txt'
    mcc_fold1 = []
    mcc_fold2 = []
   
    thresholds = [10**-i for i in range(1, 16)]
    
    preds1 = get_predictions(file1)
    preds2 = get_predictions(file2)
        
  
    print(f"{'Threshold':<10} | {'Set1 Q2':<10} | {'Set1 MCC':<10} | {'Set2 Q2':<10} | {'Set2 MCC':<10}")
    print("-" * 65)

    for th in thresholds:
        q2_1, mcc_1 = get_metrics(preds1, th)
        mcc_fold1.append(mcc_1)    

        q2_2, mcc_2 = get_metrics(preds2, th)
        mcc_fold2.append(mcc_2)
          
        print(f"{th:<10.1e} | {q2_1:<10.4f} | {mcc_1:<10.4f} | {q2_2:<10.4f} | {mcc_2:<10.4f}")

 #-----------------------------------------------new part (andamento del MCC rispetto alla threshold)---------------------------------------------------------

    plt.figure(figsize=(10, 5.5))

    plt.plot(
        thresholds, mcc_fold1, 
        marker='o', linewidth=2, color="#31b04c", label='Fold 1'
    )

    plt.plot(
        thresholds, mcc_fold2, 
        marker='s', linewidth=2, color="#f243c9", label='Fold 2'
    )

    # Linea verticale verde punteggiata per la soglia ottimale (1e-5)
    plt.axvline(
        x=1e-5, color='black', linestyle=':', linewidth=2, label='Optimal threshold (1e-5)'
    )

    # Configurazione della scala logaritmica invertita (da 10^-1 a 10^-15)
    plt.xscale('log')
    plt.gca().invert_xaxis()  # Inverte l'asse X per mostrare gli E-value da sinistra a destra (da grandi a piccoli)

    # Etichette e Titoli
    plt.title('MCC vs E-value Threshold (2-fold Cross Validation)', fontsize=14, pad=10)
    plt.xlabel('E-value threshold (log scale)', fontsize=12)
    plt.ylabel('MCC', fontsize=12)

    # Griglia e Legenda
    plt.grid(True, which="both", linestyle="-", alpha=0.3)
    plt.legend(loc='lower center', fontsize=11)

    plt.tight_layout()
    output_dir = current_file_path.parent / "output_figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir/'mcc_vs_threshold_cv.png', dpi=300)
    plt.show()
    plt.close()

#---------------------------------------Computation oF Confucion Matrix 2 for the threshold determined using 'kunitz_set_1.txt' as training and 'kunitz_set_2.txt' for Validation
    # Esecuzione: Training su 1, Test su 2
    th1, cm1 = cross_validate(preds1, preds2, "Train1_Test2", thresholds)
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Esecuzione: Training su 2, Test su 1
    th2, cm2 = cross_validate(preds2, preds1, "Train2_Test1", thresholds)
    
    fp1, fn1 = get_errors(preds2, th1)
    fp2, fn2 = get_errors(preds1, th2)

    # Somma le liste corrispondenti
    false_positive_tot = fp1 + fp2
    false_negatives_tot = fn1 + fn2

    print(false_positive_tot)
    print(false_negatives_tot)
    