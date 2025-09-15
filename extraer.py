import glob
import os
import json
import argparse
from extractor import EventExtractor
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def main():
    parser = argparse.ArgumentParser(description="Extraer eventos de textos.")
    parser.add_argument("--modelo", required=True, help="Nombre del modelo a utilizar.")
    parser.add_argument("--input_dir", default="data", help="Directorio de entrada con los archivos de texto.")
    parser.add_argument("--output_dir", default="resultados", help="Directorio de salida para los resultados.")

    args = parser.parse_args()

    extractor = EventExtractor(model_name=args.modelo, api_key=API_KEY)

    modelo_folder = f"{args.modelo}"
    output_dir_base = os.path.join(args.output_dir, modelo_folder)
    os.makedirs(output_dir_base, exist_ok=True)

    json_files = sorted(
        [f for f in os.listdir(args.input_dir) if f.endswith('.json')],
        key=lambda f: int(f.split('.')[0])
    )

    for filename in json_files:
        filepath = os.path.join(args.input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            texto = data.get('texto')

        if not texto:
            print(f"Advertencia: No se encontró la clave 'texto' en {filepath}. Saltando archivo.")
            continue

        print(f"Procesando texto de {filepath}")
        
        output = extractor.extract(texto)

        # Guardar resultados
        output_filename = os.path.join(output_dir_base, filename)
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
