PROMPT_ESPANOL_EVENTOS = """<s>[INST]
Tu tarea es identificar **eventos** en el texto original, basándote en la ontología de tipos de evento definida a continuación.

**Tipos de Evento Permitidos**:
- CAPTURA: secuestro, captura, detención o desaparición de personas.
- ASESINATO: asesinato de personas.


**Cada evento debe contener los siguientes campos**:
- "descripcion": Debe ser la frase literal o el conjunto de frases contiguas que describen el evento en el texto original, sin añadir contexto adicional ni información no relacionada con el evento específico. Siempre debe tener un valor y debe describir un evento dentro de los tipos permitidos.
- "tipo": Uno de los valores permitidos (CAPTURA, ASESINATO).
- "fecha": Valor textual que coincida exactamente con el texto y que corresponda a tipo FECHA (horas, días, meses, años, rangos o periodos de tiempo, incluyendo relativos como "día de la fecha"). Si no se menciona, usa `null`.
- "lugar": Valor textual que coincida exactamente con el texto y que corresponda a tipo LUGAR (puede ser relativo o general). Si no se menciona, usa `null`.
- "victimas": Lista de valores textuales de las entidades de tipo PERSONA afectadas por el evento. Definición de victima: Persona que sufre directamente las consecuencias del evento (captura o asesinato).
    - Si se conoce el nombre de la persona, úsalo.
    - Si se menciona una organización o grupo armado, extrae el nombre de la organización directamente y omite expresiones como "miembros de", "adeptos de", "integrantes de", etc.
    - Si no se conoce el nombre de la persona pero sí su organización o grupo, incluye el nombre de la organización o grupo (una vez por mención de grupo). Incluir esto sólo cuando no se conozca el nombre de la persona.
    - Si no se conoce el nombre de la persona ni su organización, pero se indica una cantidad o profesión (ej. "dos campesinos", "varios individuos"), utiliza esa descripción.
    - Si no se aporta información específica más allá de una existencia genérica, utiliza "otro" (singular) u "otros" (plural).
    - Si no se menciona explícitamente ninguna víctima, la lista debe ser vacía `[]`.
- "victimarios": Lista de valores textuales de las entidades de tipo PERSONA u ORGANIZACIÓN responsables del evento (incluir presuntos responsables). Definición de victimario: Persona u organización que causa o ejecuta el evento (captura o asesinato). Incluye autores materiales y quienes dan la orden.
    - Aplican las mismas reglas que para "victimas" (nombre de persona, organización, descripción genérica, "otro/s").
    - Si no se menciona explícitamente ningún victimario, la lista debe ser vacía `[]`.

**Instrucciones Estrictas**:
1.  Debes identificar y extraer **TODOS** los eventos de los tipos permitidos (CAPTURA, ASESINATO) que se mencionen explícitamente en el texto, **EN EL ORDEN** en que aparecen. No omitas ninguno.
2.  Los eventos pueden ser hechos consumados, planeados o en proceso de ejecución.
3.  ES ABSOLUTAMENTE CRÍTICO que los valores para el campo "tipo" provengan ÚNICAMENTE de la lista de "Tipos de Evento Permitidos". Si un evento no encaja estrictamente en esas categorías, NO lo incluyas. NO incluyas asaltos, robos, ataques, enfrentamientos, emboscadas, ni ningún otro tipo de evento que no esté explícitamente en la lista de tipos permitidos.
4.  Solo extrae eventos que sean mencionados directa y explícitamente en el texto original. No infieras eventos no descritos.
5.  Si para un evento no se menciona explícitamente información para los campos "fecha", "lugar", la lista de "victimas" está vacía o la lista de "victimarios" está vacía, usa `null` para "fecha" y "lugar", y listas vacías `[]` para "victimas" y "victimarios respectivamente. El campo "descripcion" siempre debe tener contenido.
6.  **Regla especial para CAPTURA**: Si se menciona que una persona "presta declaración", "es interrogada" o "está detenida" ante una autoridad, y no se ha mencionado previamente un evento de captura explícito para esa persona en ese contexto, considera esto como un evento de tipo CAPTURA. La autoridad interrogadora sería el victimario.
7.  En los eventos de tipo CAPTURA, si hay más de una mención de LUGAR, incluir sólo el LUGAR inicial.
8.  Extraer una única mención de cada PERSONA.
9.  **MUY IMPORTANTE:**Si no hay eventos válidos que cumplan con los criterios en el texto, devuelve un JSON con una clave "eventos" que contenga una lista vacía: `{{"eventos": []}}`.

**Formato de salida ESTRICTO**:
Un único objeto JSON con una clave "eventos". El valor de "eventos" debe ser una lista de objetos. Cada objeto de la lista representa un evento y debe tener las claves "descripcion", "tipo", "fecha", "lugar", "victimas" y "victimarios".

**Ejemplo de Texto**:
"RESULTADO DEL INTERROGATORIO A PERSONAS AFINES
A LUCIO CABAÑAS BARRIENTOS

A las 7.00 horas del día de la fecha llegaron al Cam-
po Militar número Uno, nueve personas detenidas por la 27/a. Zo
na Militar, con sede en Acapulco, Gro., mismas que desde hace
dos meses se encontraban detenidas por sospechar que pertene---
cían al grupo de LUCIO CABAÑAS BARRIENTOS.

Los detenidos son: ALBERTO ARROYO DIONISIO, JUSTINO
BARRIENTOS, ROMANA RIOS DE ROQUE, DAVED ROJAS ARIAS, PETRONILO-
CASTRO HERNANDEZ, GUADALUPE CASTRO MOLINA, ISABEL JIMENEZ HERNAN
DEZ, Y LUIS CABAÑAS OCAMPO.

Agentes de esta Dirección procedieron de inmediato a
interrogar a las mencionadas personas, quienes han manifestado
lo siguiente:

LUIS CABAÑAS OCAMPO, dijo ser haber nacido en la calle San Luis, Corral Fal
so, Gro., casado, de 48 años de edad, agricultor, con domicilio-
conocido en San Vicente Benítez; ser tío de LUCIO CABAÑAS BAR
RRIENTOS y saber que éste se viene dedicando a actividades sub--
versivas en contra de los Gobiernos Estatal y Federal y que uni-
camente lo liga el parentesco que con éste tiene. Que fue miem--
bro del Frente Electoral del Pueblo (FEP) y de la U.E.N., ya que su ideología es iz--
quierdista, pero que no cree que la forma de liberar al pueblo
sea mediante la lucha armada. Que está dedicado a la labor del
campo y que en algunas ocasiones ha protestado por medio de la
televisión y mediante comunicados de prensa por las arbitrarie--
dades que comete el Ejército en los poblados de las Sierras de
Guerrero, cuando realizan la labor de ubicación de su pariente
LUCIO CABAÑAS; que no participa en dicho grupo y que poco tiempo
antes de ser detenido se entrevistó con el C. Gobernador del Es-
tado, quien le ofreció su intervención para que LUCIO CABAÑAS al
canzara la amnistía, entrevista que no logró realizar con este-
último porque al poco tiempo fue detenido por el secuestro que
realizó su pariente en compañia de dos compañeros en contra de CUAUHTEMOC GARCIA TERAN y forzo
samente las autoridades de Guerrero han querido involucrarlo en-
dicho acto.

14.DIC-79

[Firma]
BARRIENTOS FLORES JUSTINO

Se tiene conocimiento que se incorporó al Partido
de los Pobres que comandaba Lucio Cabañas Barrientos, desde
principios del año de 1972.
90
Con motivo de que Lucio Cabañas Barrientos se sen--
tía acosado por elementos de la fuerza pública en la Sierra
de Guerrero y ante el temor de sus adeptos de ser capturados-
que abandonaban su causa, organizó un grupo de sujetos a quie
nes encomendó la misión específica de obligar a los deserto--
res a reincorporarse al grupo que comandaba él mismo.

Por lo anterior se sabe que a 5 días de su vuelta,
fue sustraido en forma violenta de su domicilio en Atoyac de-
Alvarez, Justino Barrientos Flores y obligado a participar en
diferentes hechos delictuosos.

El 25 de junio de 1972, resultó muerto en una embos
cada que realizaron en contra de elementos del Ejército mexi-
cano del 50/o Batallón de Infantería quienes se trasladaban a
su base de partida en San Vicente de Benitez, Gro., mismos
que al sentirse atacados repelieron la agresión dando como re
sultado la muerte de varios individuos entre los que se encon
traba este sujeto."

**Entidades ya identificadas en el texto original (Ejemplo)**:
```json
{{
  "entidades": [
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "7.00 horas del día de la fecha", "tipo": "FECHA"}},
    {{"texto": "Campo Militar número Uno", "tipo": "LUGAR"}},
    {{"texto": "27/a. Zona Militar", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Acapulco. Gro.", "tipo": "LUGAR"}},
    {{"texto": "hace dos meses", "tipo": "FECHA"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ALBERTO ARROYO DIONISIO", "tipo": "PERSONA"}},
    {{"texto": "JUSTINO BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ROMANA RIOS DE ROQUE", "tipo": "PERSONA"}},
    {{"texto": "DAVED ROJAS ARIAS", "tipo": "PERSONA"}},
    {{"texto": "PETRONILO CASTRO HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "GUADALUPE CASTRO MOLINA", "tipo": "PERSONA"}},
    {{"texto": "ISABEL JIMENEZ HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "calle San Luis. Corral Falso, Gro.", "tipo": "LUGAR"}},
    {{"texto": "San Vicente Benítez", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "Gobiernos Estatal y Federal", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Frente Electoral del Pueblo", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "FEP", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "U.E.N.", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Ejército", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Sierras de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "Gobernador del Estado", "tipo": "PERSONA"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "CUAUHTEMOC GARCIA TERAN", "tipo": "PERSONA"}},
    {{"texto": "autoridades de Guerrero", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Guerrero", "tipo": "LUGAR"}},
    {{"texto": "14.DIC-79", "tipo": "FECHA"}},
    {{"texto": "BARRIENTOS FLORES JUSTINO", "tipo": "PERSONA"}},
    {{"texto": "Partido de los Pobres", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "principios del año de 1972", "tipo": "FECHA"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "Sierra de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "a 5 días de su vuelta", "tipo": "FECHA"}},
    {{"texto": "su domicilio en Atoyac de Alvarez", "tipo": "LUGAR"}},
    {{"texto": "Justino Barrientos Flores", "tipo": "PERSONA"}},
    {{"texto": "25 de junio de 1972", "tipo": "FECHA"}},
    {{"texto": "Ejército mexi-cano", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "50/o Batallón de Infantería", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "San Vicente de Benitez, Gro.", "tipo": "LUGAR"}},
  ]
}}
```

**JSON de ejemplo esperado**:
```json
{{
  "eventos": [
    {{
      "descripcion": "A las 7.00 horas del día de la fecha llegaron al Campo Militar número Uno, nueve personas detenidas por la 27/a. Zona Militar, con sede en Acapulco, Gro.",
      "tipo": "CAPTURA",
      "fecha": "7.00 horas del día de la fecha",
      "lugar": "Campo Militar número Uno",
      "victimas": [
        "ALBERTO ARROYO DIONISIO",
        "JUSTINO BARRIENTOS",
        "ROMANA RIOS DE ROQUE",
        "DAVED ROJAS ARIAS",
        "PETRONILO CASTRO HERNANDEZ",
        "GUADALUPE CASTRO MOLINA",
        "ISABEL JIMENEZ HERNANDEZ",
        "LUIS CABAÑAS OCAMPO"
      ],
      "victimarios": ["27/a. Zona Militar"]
    }},
    {{
      "descripcion": "poco tiempo antes de ser detenido",
      "tipo": "CAPTURA",
      "fecha": "poco tiempo antes",
      "lugar": null,
      "victimas": [
        "LUIS CABAÑAS OCAMPO"
      ],
      "victimarios": []
    }},
    {{
      "descripcion": "el secuestro que realizó su pariente en compañia de dos compañeros en contra de CUAUHTEMOC GARCIA TERAN",
      "tipo": "CAPTURA",
      "fecha": null,
      "lugar": null,
      "victimas": [
        "CUAUHTEMOC GARCIA TERAN"
      ],
      "victimarios": [
        "LUCIO CABAÑAS BARRIENTOS",
        "dos compañeros"
      ]
    }},
    {{
      "descripcion": "fue sustraido en forma violenta de su domicilio en Atoyac de-Alvarez, Justino Barrientos Flores",
      "tipo": "CAPTURA",
      "fecha": "a 5 días de su vuelta",
      "lugar": "su domicilio en Atoyac de-Alvarez",
      "victimas": [
        "Justino Barrientos Flores"
      ],
      "victimarios": []
    }},
    {{
      "descripcion": "El 25 de junio de 1972, resultó muerto en una emboscada que realizaron en contra de elementos del Ejército mexicano del 50/o Batallón de Infantería quienes se trasladaban a su base de partida en San Vicente de Benitez, Gro., mismos que al sentirse atacados repelieron la agresión dando como resultado la muerte de varios individuos entre los que se encontraba este sujeto.",
      "tipo": "ASESINATO",
      "fecha": "25 de junio de 1972",
      "lugar": "San Vicente de Benitez, Gro.",
      "victimas": [
        "Justino Barrientos Flores", "varios individuos"
      ],
      "victimarios": [
        "Ejército mexicano", "50/o Batallón de Infantería"
      ]
    }}
  ]
}}
```

Utiliza las entidades previamente extraídas como base para completar los campos.


Ahora, procesa el siguiente texto y genera el JSON correspondiente:

**Texto**:
"{texto_entrada}"

Entidades ya identificadas en el texto original:
```json
{entidades_extraidas_str}
```

**JSON**:
[/INST]"""

PROMPT_ESPANOL_EVENTOS_SIN_DESC = """<s>[INST]
Tu tarea es identificar **eventos** en el texto original, basándote en la ontología de tipos de evento definida a continuación.

**Tipos de Evento Permitidos**:
- CAPTURA: secuestro, captura, detención o desaparición de personas.
- ASESINATO: asesinato de personas.


**Cada evento debe contener los siguientes campos**:
- "tipo": Uno de los valores permitidos (CAPTURA, ASESINATO).
- "fecha": Valor textual que coincida exactamente con el texto y que corresponda a tipo FECHA (horas, días, meses, años, rangos o periodos de tiempo, incluyendo relativos como "día de la fecha"). Si no se menciona, usa `null`.
- "lugar": Valor textual que coincida exactamente con el texto y que corresponda a tipo LUGAR (puede ser relativo o general). Si no se menciona, usa `null`.
- "victimas": Lista de valores textuales de las entidades de tipo PERSONA afectadas por el evento. Definición de victima: Persona que sufre directamente las consecuencias del evento (captura o asesinato).
    - Si se conoce el nombre de la persona, úsalo.
    - Si se menciona una organización o grupo armado, extrae el nombre de la organización directamente y omite expresiones como "miembros de", "adeptos de", "integrantes de", etc.
    - Si no se conoce el nombre de la persona pero sí su organización o grupo, incluye el nombre de la organización o grupo (una vez por mención de grupo). Incluir esto sólo cuando no se conozca el nombre de la persona.
    - Si no se conoce el nombre de la persona ni su organización, pero se indica una cantidad o profesión (ej. "dos campesinos", "varios individuos"), utiliza esa descripción.
    - Si no se aporta información específica más allá de una existencia genérica, utiliza "otro" (singular) u "otros" (plural).
    - Si no se menciona explícitamente ninguna víctima, la lista debe ser vacía `[]`.
- "victimarios": Lista de valores textuales de las entidades de tipo PERSONA u ORGANIZACIÓN responsables del evento (incluir presuntos responsables). Definición de victimario: Persona u organización que causa o ejecuta el evento (captura o asesinato). Incluye autores materiales y quienes dan la orden.
    - Aplican las mismas reglas que para "victimas" (nombre de persona, organización, descripción genérica, "otro/s").
    - Si no se menciona explícitamente ningún victimario, la lista debe ser vacía `[]`.

**Instrucciones Estrictas**:
1.  Debes identificar y extraer **TODOS** los eventos de los tipos permitidos (CAPTURA, ASESINATO) que se mencionen explícitamente en el texto, **EN EL ORDEN** en que aparecen. No omitas ninguno.
2.  Los eventos pueden ser hechos consumados, planeados o en proceso de ejecución.
3.  ES ABSOLUTAMENTE CRÍTICO que los valores para el campo "tipo" provengan ÚNICAMENTE de la lista de "Tipos de Evento Permitidos". Si un evento no encaja estrictamente en esas categorías, NO lo incluyas. NO incluyas asaltos, robos, ataques, enfrentamientos, emboscadas, ni ningún otro tipo de evento que no esté explícitamente en la lista de tipos permitidos.
4.  Solo extrae eventos que sean mencionados directa y explícitamente en el texto original. No infieras eventos no descritos.
5.  Si para un evento no se menciona explícitamente información para los campos "fecha", "lugar", la lista de "victimas" está vacía o la lista de "victimarios" está vacía, usa `null` para "fecha" y "lugar", y listas vacías `[]` para "victimas" y "victimarios" respectivamente.
6.  **Regla especial para CAPTURA**: Si se menciona que una persona "presta declaración", "es interrogada" o "está detenida" ante una autoridad, y no se ha mencionado previamente un evento de captura explícito para esa persona en ese contexto, considera esto como un evento de tipo CAPTURA. La autoridad interrogadora sería el victimario.
7.  En los eventos de tipo CAPTURA, si hay más de una mención de LUGAR, incluir sólo el LUGAR inicial.
8.  Extraer una única mención de cada PERSONA.
9.  **MUY IMPORTANTE:**Si no hay eventos válidos que cumplan con los criterios en el texto, devuelve un JSON con una clave "eventos" que contenga una lista vacía: `{{"eventos": []}}`.

**Formato de salida ESTRICTO**:
Un único objeto JSON con una clave "eventos". El valor de "eventos" debe ser una lista de objetos. Cada objeto de la lista representa un evento y debe tener las claves "tipo", "fecha", "lugar", "victimas" y "victimarios".

**Ejemplo de Texto**:
"RESULTADO DEL INTERROGATORIO A PERSONAS AFINES
A LUCIO CABAÑAS BARRIENTOS

A las 7.00 horas del día de la fecha llegaron al Cam-
po Militar número Uno, nueve personas detenidas por la 27/a. Zo
na Militar, con sede en Acapulco, Gro., mismas que desde hace
dos meses se encontraban detenidas por sospechar que pertene---
cían al grupo de LUCIO CABAÑAS BARRIENTOS.

Los detenidos son: ALBERTO ARROYO DIONISIO, JUSTINO
BARRIENTOS, ROMANA RIOS DE ROQUE, DAVED ROJAS ARIAS, PETRONILO-
CASTRO HERNANDEZ, GUADALUPE CASTRO MOLINA, ISABEL JIMENEZ HERNAN
DEZ, Y LUIS CABAÑAS OCAMPO.

Agentes de esta Dirección procedieron de inmediato a
interrogar a las mencionadas personas, quienes han manifestado
lo siguiente:

LUIS CABAÑAS OCAMPO, dijo ser haber nacido en la calle San Luis, Corral Fal
so, Gro., casado, de 48 años de edad, agricultor, con domicilio-
conocido en San Vicente Benítez; ser tío de LUCIO CABAÑAS BAR
RRIENTOS y saber que éste se viene dedicando a actividades sub--
versivas en contra de los Gobiernos Estatal y Federal y que uni-
camente lo liga el parentesco que con éste tiene. Que fue miem--
bro del Frente Electoral del Pueblo (FEP) y de la U.E.N., ya que su ideología es iz--
quierdista, pero que no cree que la forma de liberar al pueblo
sea mediante la lucha armada. Que está dedicado a la labor del
campo y que en algunas ocasiones ha protestado por medio de la
televisión y mediante comunicados de prensa por las arbitrarie--
dades que comete el Ejército en los poblados de las Sierras de
Guerrero, cuando realizan la labor de ubicación de su pariente
LUCIO CABAÑAS; que no participa en dicho grupo y que poco tiempo
antes de ser detenido se entrevistó con el C. Gobernador del Es-
tado, quien le ofreció su intervención para que LUCIO CABAÑAS al
canzara la amnistía, entrevista que no logró realizar con este-
último porque al poco tiempo fue detenido por el secuestro que
realizó su pariente en compañia de dos compañeros en contra de CUAUHTEMOC GARCIA TERAN y forzo
samente las autoridades de Guerrero han querido involucrarlo en-
dicho acto.

14.DIC-79

[Firma]
BARRIENTOS FLORES JUSTINO

Se tiene conocimiento que se incorporó al Partido
de los Pobres que comandaba Lucio Cabañas Barrientos, desde
principios del año de 1972.
90
Con motivo de que Lucio Cabañas Barrientos se sen--
tía acosado por elementos de la fuerza pública en la Sierra
de Guerrero y ante el temor de sus adeptos de ser capturados-
que abandonaban su causa, organizó un grupo de sujetos a quie
nes encomendó la misión específica de obligar a los deserto--
res a reincorporarse al grupo que comandaba él mismo.

Por lo anterior se sabe que a 5 días de su vuelta,
fue sustraido en forma violenta de su domicilio en Atoyac de-
Alvarez, Justino Barrientos Flores y obligado a participar en
diferentes hechos delictuosos.

El 25 de junio de 1972, resultó muerto en una embos
cada que realizaron en contra de elementos del Ejército mexi-
cano del 50/o Batallón de Infantería quienes se trasladaban a
su base de partida en San Vicente de Benitez, Gro., mismos
que al sentirse atacados repelieron la agresión dando como re
sultado la muerte de varios individuos entre los que se encon
traba este sujeto."

**Entidades ya identificadas en el texto original (Ejemplo)**:
```json
{{
  "entidades": [
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "7.00 horas del día de la fecha", "tipo": "FECHA"}},
    {{"texto": "Campo Militar número Uno", "tipo": "LUGAR"}},
    {{"texto": "27/a. Zona Militar", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Acapulco. Gro.", "tipo": "LUGAR"}},
    {{"texto": "hace dos meses", "tipo": "FECHA"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ALBERTO ARROYO DIONISIO", "tipo": "PERSONA"}},
    {{"texto": "JUSTINO BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ROMANA RIOS DE ROQUE", "tipo": "PERSONA"}},
    {{"texto": "DAVED ROJAS ARIAS", "tipo": "PERSONA"}},
    {{"texto": "PETRONILO CASTRO HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "GUADALUPE CASTRO MOLINA", "tipo": "PERSONA"}},
    {{"texto": "ISABEL JIMENEZ HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "calle San Luis. Corral Falso, Gro.", "tipo": "LUGAR"}},
    {{"texto": "San Vicente Benítez", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "Gobiernos Estatal y Federal", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Frente Electoral del Pueblo", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "FEP", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "U.E.N.", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Ejército", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Sierras de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "Gobernador del Estado", "tipo": "PERSONA"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "CUAUHTEMOC GARCIA TERAN", "tipo": "PERSONA"}},
    {{"texto": "autoridades de Guerrero", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Guerrero", "tipo": "LUGAR"}},
    {{"texto": "14.DIC-79", "tipo": "FECHA"}},
    {{"texto": "BARRIENTOS FLORES JUSTINO", "tipo": "PERSONA"}},
    {{"texto": "Partido de los Pobres", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "principios del año de 1972", "tipo": "FECHA"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "Sierra de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "a 5 días de su vuelta", "tipo": "FECHA"}},
    {{"texto": "su domicilio en Atoyac de Alvarez", "tipo": "LUGAR"}},
    {{"texto": "Justino Barrientos Flores", "tipo": "PERSONA"}},
    {{"texto": "25 de junio de 1972", "tipo": "FECHA"}},
    {{"texto": "Ejército mexi-cano", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "50/o Batallón de Infantería", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "San Vicente de Benitez, Gro.", "tipo": "LUGAR"}},
  ]
}}
```

**JSON de ejemplo esperado**:
```json
{{
  "eventos": [
    {{
      "tipo": "CAPTURA",
      "fecha": "7.00 horas del día de la fecha",
      "lugar": "Campo Militar número Uno",
      "victimas": [
        "ALBERTO ARROYO DIONISIO",
        "JUSTINO BARRIENTOS",
        "ROMANA RIOS DE ROQUE",
        "DAVED ROJAS ARIAS",
        "PETRONILO CASTRO HERNANDEZ",
        "GUADALUPE CASTRO MOLINA",
        "ISABEL JIMENEZ HERNANDEZ",
        "LUIS CABAÑAS OCAMPO"
      ],
      "victimarios": ["27/a. Zona Militar"]
    }},
    {{
      "tipo": "CAPTURA",
      "fecha": "poco tiempo antes",
      "lugar": null,
      "victimas": [
        "LUIS CABAÑAS OCAMPO"
      ],
      "victimarios": []
    }},
    {{
      "tipo": "CAPTURA",
      "fecha": null,
      "lugar": null,
      "victimas": [
        "CUAUHTEMOC GARCIA TERAN"
      ],
      "victimarios": [
        "LUCIO CABAÑAS BARRIENTOS",
        "dos compañeros"
      ]
    }},
    {{
      "tipo": "CAPTURA",
      "fecha": "a 5 días de su vuelta",
      "lugar": "su domicilio en Atoyac de-Alvarez",
      "victimas": [
        "Justino Barrientos Flores"
      ],
      "victimarios": []
    }},
    {{
      "tipo": "ASESINATO",
      "fecha": "25 de junio de 1972",
      "lugar": "San Vicente de Benitez, Gro.",
      "victimas": [
        "Justino Barrientos Flores", "varios individuos"
      ],
      "victimarios": [
        "Ejército mexicano", "50/o Batallón de Infantería"
      ]
    }}
  ]
}}
```

Utiliza las entidades previamente extraídas como base para completar los campos.


Ahora, procesa el siguiente texto y genera el JSON correspondiente:

**Texto**:
"{texto_entrada}"

Entidades ya identificadas en el texto original:
```json
{entidades_extraidas_str}
```

**JSON**:
[/INST]"""

PROMPT_ENTIDADES_EVENTOS = """<s>[INST]
Tu tarea es extraer todas las entidades del texto proporcionado. No omitas ninguna mención.
Las entidades deben ser de los siguientes tipos: PERSONA, ORGANIZACIÓN, LUGAR, FECHA.

**Nota importante:** 
Extraer TODAS las menciones de la misma entidad como estén escritas.
Cualquier referencia a un día, fecha, momento temporal o periodo debe clasificarse como **FECHA**. Esto incluye nombres de días, meses, años, fechas completas o parciales, expresiones como "ayer", "el próximo martes", "en 1994", "hace dos semanas", etc.
Las edades NO deben clasificarse como FECHA.
Si una entidad tiene alias, inclúyelos como otra entidad aparte.
Para el tipo PERSONA, no incluir profesiones, cargos o títulos, solo nombres propios.
Para el tipo ORGANIZACIÓN, incluir nombres de instituciones, empresas, grupos políticos, etc.
Para el tipo ORGANIZACIÓN, extraer siglas y nombre de la organización por separado.
Para el tipo FECHA, extraer el fragmento más específico posible.
Para el tipo LUGAR, extraer el fragmento más específico posible. Esto puede incluir un lugar relativo, como la casa de alguien aunque no se mencione la ubicación exacta.
Si se menciona un grupo de nombres de lugares o instituciones enumerados juntos (por ejemplo: "las calles Fuerte Grande, Mineto y Funesti"), extraerlos en conjunto (la salida debe ser: "calles Fuerte Grande, Mineto y Funesti").
Extraer direcciones (calle y número), barrios, ciudades, etc. en conjunto si están concatenadas.

Formato de salida ESTRICTO: JSON con una clave "entidades" que contenga una lista de objetos, donde cada objeto tiene "texto" y "tipo".
**ASEGÚRATE DE QUE EL JSON SEA VÁLIDO.** No incluyas comentarios, explicaciones ni ningún texto fuera del bloque JSON.

Ejemplo:
Texto de Ejemplo: "RESULTADO DEL INTERROGATORIO A PERSONAS AFINES
A LUCIO CABAÑAS BARRIENTOS

A las 7.00 horas del día de la fecha llegaron al Cam-
po Militar número Uno, nueve personas detenidas por la 27/a. Zo
na Militar, con sede en Acapulco, Gro., mismas que desde hace
dos meses se encontraban detenidas por sospechar que pertene---
cían al grupo de LUCIO CABAÑAS BARRIENTOS.

Los detenidos son: ALBERTO ARROYO DIONISIO, JUSTINO
BARRIENTOS, ROMANA RIOS DE ROQUE, DAVED ROJAS ARIAS, PETRONILO-
CASTRO HERNANDEZ, GUADALUPE CASTRO MOLINA, ISABEL JIMENEZ HERNAN
DEZ, Y LUIS CABAÑAS OCAMPO.

Agentes de esta Dirección procedieron de inmediato a
interrogar a las mencionadas personas, quienes han manifestado
lo siguiente:

LUIS CABAÑAS OCAMPO, dijo ser haber nacido en la calle San Luis, Corral Fal
so, Gro., casado, de 48 años de edad, agricultor, con domicilio-
conocido en San Vicente Benítez; ser tío de LUCIO CABAÑAS BAR
RRIENTOS y saber que éste se viene dedicando a actividades sub--
versivas en contra de los Gobiernos Estatal y Federal y que uni-
camente lo liga el parentesco que con éste tiene. Que fue miem--
bro del Frente Electoral del Pueblo (FEP) y de la U.E.N., ya que su ideología es iz--
quierdista, pero que no cree que la forma de liberar al pueblo
sea mediante la lucha armada. Que está dedicado a la labor del
campo y que en algunas ocasiones ha protestado por medio de la
televisión y mediante comunicados de prensa por las arbitrarie--
dades que comete el Ejército en los poblados de las Sierras de
Guerrero, cuando realizan la labor de ubicación de su pariente
LUCIO CABAÑAS; que no participa en dicho grupo y que poco tiempo
antes de ser detenido se entrevistó con el C. Gobernador del Es-
tado, quien le ofreció su intervención para que LUCIO CABAÑAS al
canzara la amnistía, entrevista que no logró realizar con este-
último porque al poco tiempo fue detenido por el secuestro que
realizó su pariente en compañia de dos compañeros en contra de CUAUHTEMOC GARCIA TERAN y forzo
samente las autoridades de Guerrero han querido involucrarlo en-
dicho acto.

14.DIC-79

[Firma]
BARRIENTOS FLORES JUSTINO

Se tiene conocimiento que se incorporó al Partido
de los Pobres que comandaba Lucio Cabañas Barrientos, desde
principios del año de 1972.
90
Con motivo de que Lucio Cabañas Barrientos se sen--
tía acosado por elementos de la fuerza pública en la Sierra
de Guerrero y ante el temor de sus adeptos de ser capturados-
que abandonaban su causa, organizó un grupo de sujetos a quie
nes encomendó la misión específica de obligar a los deserto--
res a reincorporarse al grupo que comandaba él mismo.

Por lo anterior se sabe que a 5 días de su vuelta,
fue sustraido en forma violenta de su domicilio en Atoyac de-
Alvarez, Justino Barrientos Flores y obligado a participar en
diferentes hechos delictuosos.

El 25 de junio de 1972, resultó muerto en una embos
cada que realizaron en contra de elementos del Ejército mexi-
cano del 50/o Batallón de Infantería quienes se trasladaban a
su base de partida en San Vicente de Benitez, Gro., mismos
que al sentirse atacados repelieron la agresión dando como re
sultado la muerte de varios individuos entre los que se encon
traba este sujeto."


JSON de Ejemplo Esperado:
```json
{{
  "entidades": [
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "7.00 horas del día de la fecha", "tipo": "FECHA"}},
    {{"texto": "Campo Militar número Uno", "tipo": "LUGAR"}},
    {{"texto": "27/a. Zona Militar", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Acapulco. Gro.", "tipo": "LUGAR"}},
    {{"texto": "hace dos meses", "tipo": "FECHA"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ALBERTO ARROYO DIONISIO", "tipo": "PERSONA"}},
    {{"texto": "JUSTINO BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "ROMANA RIOS DE ROQUE", "tipo": "PERSONA"}},
    {{"texto": "DAVED ROJAS ARIAS", "tipo": "PERSONA"}},
    {{"texto": "PETRONILO CASTRO HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "GUADALUPE CASTRO MOLINA", "tipo": "PERSONA"}},
    {{"texto": "ISABEL JIMENEZ HERNANDEZ", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "LUIS CABAÑAS OCAMPO", "tipo": "PERSONA"}},
    {{"texto": "calle San Luis. Corral Falso, Gro.", "tipo": "LUGAR"}},
    {{"texto": "San Vicente Benítez", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS BARRIENTOS", "tipo": "PERSONA"}},
    {{"texto": "Gobiernos Estatal y Federal", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Frente Electoral del Pueblo", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "FEP", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "U.E.N.", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Ejército", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Sierras de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "Gobernador del Estado", "tipo": "PERSONA"}},
    {{"texto": "LUCIO CABAÑAS", "tipo": "PERSONA"}},
    {{"texto": "CUAUHTEMOC GARCIA TERAN", "tipo": "PERSONA"}},
    {{"texto": "autoridades de Guerrero", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Guerrero", "tipo": "LUGAR"}},
    {{"texto": "14.DIC-79", "tipo": "FECHA"}},
    {{"texto": "BARRIENTOS FLORES JUSTINO", "tipo": "PERSONA"}},
    {{"texto": "Partido de los Pobres", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "principios del año de 1972", "tipo": "FECHA"}},
    {{"texto": "Lucio Cabañas Barrientos", "tipo": "PERSONA"}},
    {{"texto": "Sierra de Guerrero", "tipo": "LUGAR"}},
    {{"texto": "a 5 días de su vuelta", "tipo": "FECHA"}},
    {{"texto": "su domicilio en Atoyac de Alvarez", "tipo": "LUGAR"}},
    {{"texto": "Justino Barrientos Flores", "tipo": "PERSONA"}},
    {{"texto": "25 de junio de 1972", "tipo": "FECHA"}},
    {{"texto": "Ejército mexi-cano", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "50/o Batallón de Infantería", "tipo": "ORGANIZACIÓN"}},
    {{"texto": "San Vicente de Benitez, Gro.", "tipo": "LUGAR"}},
  ]
}}
```

Ahora, procesa el siguiente texto y genera el JSON correspondiente:

Texto:
"{texto_entrada}"

JSON:
[/INST]"""