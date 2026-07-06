import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_curve, auc
from compute_performances import find_best_threshold, get_predictions

current_file_path = Path(__file__).resolve() 
output_dir = current_file_path.parent / "output_figures"
output_dir.mkdir(parents=True, exist_ok=True)





if __name__ == '__main__':
    thresholds = [10**-i for i in range(1, 16)]

    file1 =current_file_path.parent/'kunitz_set_1.txt'
    file2 =current_file_path.parent/'kunitz_set_2.txt'

    preds1 = get_predictions(file1)
    preds2 = get_predictions(file2)
    # y_true: the real classes (0 or 1)
    # y_scores: the "negated" e-values (because smaller e-value = higher probability)
   
    y_true1 = [p[2] for p in preds1]
    # We use -log10 of e-value because roc_curve expects higher values for positive class
    y_scores1 = [-np.log10(p[1] if p[1] > 0 else 1e-200) for p in preds1]

    y_true2 = [p[2] for p in preds2]
    # We use -log10 of e-value because roc_curve expects higher values for positive class
    y_scores2 = [-np.log10(p[1] if p[1] > 0 else 1e-200) for p in preds2]

    best_th1 = find_best_threshold(preds2, thresholds)
    best_th2=find_best_threshold(preds1, thresholds)
#----------------------------------------ROC CURVE calculation ------------------------------------------------------
    # 2. Calculate ROC
    fpr1, tpr1, thresholds1 = roc_curve(y_true1, y_scores1)
    roc_auc1 = auc(fpr1, tpr1)

    fpr2, tpr2, thresholds2 = roc_curve(y_true2, y_scores2)
    roc_auc2 = auc(fpr2, tpr2)

    # Trova l'indice del valore di soglia più vicino alla tua best_th
    idx = np.argmin(np.abs(thresholds1 + np.log10(best_th1)))#

    # Recupera le coordinate FPR e TPR a quell'indice
    best_fpr1 = fpr1[idx]
    best_tpr1 = tpr1[idx]

    idx = np.argmin(np.abs(thresholds2 + np.log10(best_th2)))#

    # Recupera le coordinate FPR e TPR a quell'indice
    best_fpr2 = fpr2[idx]
    best_tpr2 = tpr2[idx]
    
    # 3. Plotting
    plt.figure()
    plt.xscale('linear')
    
#----------------------------ROC CURVE DEL SET2 (utilizzando set1 come training)-------------------------------------
    plt.plot(fpr2, tpr2, color='#f243c9', label=f'ROC curve (area = {roc_auc2:.4f})')
    plt.scatter(best_fpr1, best_tpr1, color='red', marker='o', s=100, zorder=5, label=f'Best Threshold ({best_th1:.1e})')

    plt.legend(loc="lower right")
    plt.plot([0, 1], [0, 1], color='black', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Kunitz2 HMM')
    plt.legend(loc="lower right")
    plt.savefig(output_dir/'kunitz_roc_curve2.png', dpi=300)
    plt.show()
    plt.close()
#----------------------------ROC CURVE DEL SET1 (utilizzando set2 come training)-------------------------------------
    plt.plot(fpr1, tpr1, color="#31b04c", label=f'ROC curve (area = {roc_auc1:.4f})')
    plt.scatter(best_fpr2, best_tpr2, color='red', marker='o', s=100, zorder=5, label=f'Best Threshold ({best_th2:.1e})')
    plt.plot([0, 1], [0, 1], color='black', linestyle='--')
  

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Kunitz1 HMM')
    plt.legend(loc="lower right")
    plt.savefig(output_dir/'kunitz_roc_curve1.png', dpi=300)
    plt.show()
    plt.close()