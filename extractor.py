import json
import re
import time
from google import genai
from google.genai import types
from prompts import PROMPT_ENTIDADES_EVENTOS, PROMPT_ESPANOL_EVENTOS


class EventExtractor:
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(tools=[])

    def _parse_json(self, generated_text, prompt_type="other"):
        # --- Mejorar el parsing JSON ---
        json_string = ""
        try:
            # 1. Buscar bloques de código JSON (```json ... ```)
            json_match = re.search(r"```json(.*?)```", generated_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                # 2. Si no hay bloques de código, intentar encontrar el primer/último objeto JSON/array
                # Buscar el inicio del JSON (puede ser { o [)
                json_start_index = -1
                first_curly = generated_text.find('{')
                first_square = generated_text.find('[')

                if first_curly != -1 and (first_square == -1 or first_curly < first_square):
                    json_start_index = first_curly
                elif first_square != -1:
                    json_start_index = first_square

                # Buscar el final del JSON (puede ser } o ])
                json_end_index = -1
                last_curly = generated_text.rfind('}')
                last_square = generated_text.rfind(']')

                if last_curly != -1 and (last_square == -1 or last_curly > last_square):
                    json_end_index = last_curly + 1
                elif last_square != -1:
                    json_end_index = last_square + 1

                if json_start_index != -1 and json_end_index != -1 and json_end_index > json_start_index:
                    json_string = generated_text[json_start_index:json_end_index].strip()
                else:
                    raise ValueError("No se encontró un objeto JSON o array válido.")

            # Intentar parsear el JSON
            parsed_output = json.loads(json_string)
            return parsed_output
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decodificando JSON: {e}")
            print(f"Salida problemática (intentando parsear): '{json_string[:500] if json_string else generated_text[:500]}'...")

            if prompt_type:
                return {prompt_type: []}
            else:
                return {}

    def _extract_entities(self, text):
        print("Generando entidades...")
        prompt = PROMPT_ENTIDADES_EVENTOS.format(texto_entrada=text)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )
        print(str(response))
        time.sleep(15)
        return self._parse_json(response.text, prompt_type="entities")

    def _extract_events(self, text, entities):
        print("Generando eventos...")
        prompt = PROMPT_ESPANOL_EVENTOS.format(
            texto_entrada=text,
            entidades_extraidas_str=json.dumps(entities, ensure_ascii=False, indent=2)
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )
        print(response)
        time.sleep(18)
        return self._parse_json(response.text, prompt_type="events")

    def extract(self, text):
        entities_response = self._extract_entities(text)
        entities = entities_response.get('entidades', []) if isinstance(entities_response, dict) else []

        events_response = self._extract_events(text, entities)
        events = events_response.get('eventos', []) if isinstance(events_response, dict) else []

        return {
            "entidades": entities,
            "eventos": events,
        }
