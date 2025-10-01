import argparse
import os
import json
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
from typing import Dict, Any, List, Tuple, Set

def fuzzy_match(text1, text2, threshold=0.85):
    similarity = SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()
    return similarity >= threshold

def evaluar_extraccion_evento(
    evento_gt: Dict[str, Any],
    evento_pred: Dict[str, Any],
    threshold: float = 0.85,
    campos_excluidos: Set[str] = {"descripcion", "tipo"},
    #valores_ignorados: Set[str] = {"otro", "otros"}
    ) -> Dict[str, Any]:
    """
    Calcula las métricas de precisión, recall y F1 para cada campo del evento.
    """
    campos = [campo for campo in evento_gt.keys() if campo not in campos_excluidos]
    
    resultados = {}
    sum_precisiones, sum_recalls, sum_f1_scores = 0.0, 0.0, 0.0

    for campo in campos:
        # Normalizar valores a listas
        valor_gt = evento_gt.get(campo) or []
        valor_pred = evento_pred.get(campo) or []

        if isinstance(valor_gt, str):
            valor_gt = [valor_gt] if valor_gt else []
            valor_pred = [valor_pred] if valor_pred else []

        if valor_pred == ["otro"] or valor_pred == ["otros"]:
            valor_pred = []

        if valor_gt == valor_pred == []:
            precision, recall, f1_score = 1.0, 1.0, 1.0
        else:

            matched_pred = set()
            matched_gold = set()
                
            for i, pred in enumerate(valor_pred):
                for j, gold in enumerate(valor_gt):
                    if fuzzy_match(pred, gold, threshold):
                        if i not in matched_pred and j not in matched_gold:
                            matched_pred.add(i)
                            matched_gold.add(j)
                            break

            tp = len(matched_pred)
            fp = len(valor_pred) - tp
            fn = len(valor_gt) - tp

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        resultados[campo] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
        sum_precisiones += precision
        sum_recalls += recall
        sum_f1_scores += f1_score

    num_campos = len(campos)
    resultados["totales"] = {
        'precision': sum_precisiones / num_campos,
        'recall': sum_recalls / num_campos,
        'f1_score': sum_f1_scores / num_campos
    }
    return resultados


def main():
    parser = argparse.ArgumentParser(description="Evaluar la extracción de eventos.")
    parser.add_argument("--modelo", required=True, help="Nombre del modelo a utilizar.")
    parser.add_argument("--input_dir", default="data", help="Directorio con los datos de ground truth.")
    parser.add_argument("--results_dir", default="resultados", help="Directorio base de los resultados.")

    args = parser.parse_args()

    # Cargar eventos ground truth
    eventos_gt = []
    json_files_gt = sorted(
        [f for f in os.listdir(args.input_dir) if f.endswith('.json')],
        key=lambda f: int(f.split('.')[0])
    )
    for filename in json_files_gt:
        filepath = os.path.join(args.input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            eventos_gt.append(data.get('eventos', []))

    # Cargar eventos predecidos
    modelo_dir = os.path.join(args.results_dir, args.modelo)
    eventos_pred = []
    json_files_pred = sorted(
        [f for f in os.listdir(modelo_dir) if f.endswith('.json')],
        key=lambda f: int(f.split('.')[0])
    )
    for filename in json_files_pred:
        filepath = os.path.join(modelo_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            eventos_pred.append(data.get('eventos', []))

    tp_count, fp_count, fn_count = 0, 0, 0

    precision_total_campos = defaultdict(float)
    recall_total_campos = defaultdict(float)
    campos_unicos = set() # Para mantener un registro de todos los campos encontrados

    for doc_idx, (eventos_gt_doc, eventos_pred_doc) in enumerate(zip(eventos_gt, eventos_pred)):
        print(f"Documento {doc_idx + 1}")

        num_gt = len(eventos_gt_doc)
        num_pred = len(eventos_pred_doc)

        tp = min(num_gt, num_pred)
        fn = num_gt - tp 
        fp = num_pred - tp

        fn_count += fn
        fp_count += fp
        
        # Pre-inicializar la estructura para las matrices de métricas
        # La clave será el nombre del campo (ej. 'fecha', 'totales')
        # El valor será otro diccionario con las matrices de 'precision', 'recall' y 'f1_score'
        matrices_por_campo = defaultdict(lambda: {
            'precision': np.zeros((num_gt, num_pred)),
            'recall': np.zeros((num_gt, num_pred)),
            'f1_score': np.zeros((num_gt, num_pred))
        })

        for i, evento_gt in enumerate(eventos_gt_doc):
            for j, evento_pred in enumerate(eventos_pred_doc):
                # Solo se calculan métricas si los tipos de evento coinciden
                if evento_gt.get('tipo') == evento_pred.get('tipo'):
                    metricas_par = evaluar_extraccion_evento(evento_gt, evento_pred, threshold=0.85)
                    
                    # Poblar las matrices para cada campo y métrica
                    for campo, valores_metricas in metricas_par.items():
                        campos_unicos.add(campo) # Añadir el campo al set global
                        matrices_por_campo[campo]['precision'][i, j] = valores_metricas['precision']
                        matrices_por_campo[campo]['recall'][i, j] = valores_metricas['recall']
                        matrices_por_campo[campo]['f1_score'][i, j] = valores_metricas['f1_score']

        # Realizar la asignación usando la matriz F1 de 'totales'
        f1_matrix_totales = matrices_por_campo['totales']['f1_score']
        
        # El algoritmo de asignación encuentra los pares óptimos (GT, Pred)
        asignacion_filas, asignacion_cols = linear_sum_assignment(f1_matrix_totales, maximize=True)

        # Acumular las métricas de los pares asignados
        if tp > 0:
            tp_count += tp
            mean_f1_asignados = f1_matrix_totales[asignacion_filas, asignacion_cols].mean()
            print(f"F1-score promedio de los eventos asignados: {mean_f1_asignados:.4f}")

            for campo in matrices_por_campo:
                # Sumar la precisión de los pares asignados para este campo
                precision_asignada = matrices_por_campo[campo]['precision'][asignacion_filas, asignacion_cols].sum()
                precision_total_campos[campo] += precision_asignada

                # Sumar el recall de los pares asignados para este campo
                recall_asignado = matrices_por_campo[campo]['recall'][asignacion_filas, asignacion_cols].sum()
                recall_total_campos[campo] += recall_asignado
        
        print("---------------------------------")


    print(f"Conteo total de eventos: TP={tp_count}, FP={fp_count}, FN={fn_count}")
    print("\nMétricas finales por campo:")

    campos_a_imprimir = sorted([c for c in campos_unicos if c != 'totales']) + ['totales']

    for campo in campos_a_imprimir:
        print(f"===== Campo: {campo.upper()} =====")
        
        # El denominador para precisión es el total de eventos predichos (TP + FP)
        # El denominador para recall es el total de eventos ground truth (TP + FN)
        # Usamos los conteos a nivel de evento, que es una métrica estándar (macro-promedio)
        denominador_precision = tp_count + fp_count
        denominador_recall = tp_count + fn_count

        precision_final = precision_total_campos[campo] / denominador_precision if denominador_precision > 0 else 0.0
        recall_final = recall_total_campos[campo] / denominador_recall if denominador_recall > 0 else 0.0
        
        numerador_f1 = 2 * precision_final * recall_final
        denominador_f1 = precision_final + recall_final
        f1_final = numerador_f1 / denominador_f1 if denominador_f1 > 0 else 0.0

        print(f"  Precisión final: {precision_final:.4f}")
        print(f"  Recall final:    {recall_final:.4f}")
        print(f"  F1-Score final:  {f1_final:.4f}")
        print("="*25)

if __name__ == "__main__":
    main()
