# Guía Técnica de Evaluación de IA Agéntica (ES)

Esta guía documenta la implementación del repositorio para:

- `01_deepeval_agent_eval.py`
- `02_inspect_ai_agent_eval.py`
- `03_azure_ai_eval_agents.py`

Se enfoca en tres objetivos:

1. Conceptos base detrás de la evaluación de agentes.
2. Cómo cada librería aterriza esos conceptos en APIs concretas.
3. Cómo está estructurado cada script y por qué existe cada sección.

---

## 1. Línea Base Conceptual: Qué Estás Evaluando

La evaluación de agentes es distinta a la evaluación de LLMs de un solo turno, porque la calidad no depende solo del texto final.

En agentes, normalmente evalúas estas dimensiones:

- `comprensión de intención`: ¿el agente entendió el objetivo del usuario?
- `cumplimiento/adherencia de tarea`: ¿resolvió realmente lo solicitado?
- `comportamiento de herramientas`: ¿llamó las herramientas correctas con argumentos y secuencia correctos?
- `calidad de respuesta`: relevancia, coherencia, fluidez, factualidad.
- `seguridad`: contenido dañino, prompt injection, violaciones de política.
- `comportamiento operacional`: confiabilidad, latencia, costo, regresiones entre versiones.

Los tres scripts cubren intencionalmente distintos niveles de este stack:

- `DeepEval`: enfoque test-first y estilo CI, parecido a pytest.
- `Inspect AI`: framework de evaluación por tareas (Dataset -> Solver -> Scorer) con énfasis en agentes/herramientas.
- `Azure AI Evaluation SDK`: APIs de evaluación centradas en calidad/seguridad, incluyendo métricas agénticas y batch `evaluate()`.

---

## 2. Entorno y Configuración

Desde la raíz del workspace:

```bash
pip install -r requirements.txt
```

`requirements.txt` actualmente incluye:

- `deepeval>=3.0.0`
- `inspect-ai>=0.3.130`
- `azure-ai-evaluation>=1.0.0`
- `azure-identity>=1.15.0`
- `python-dotenv>=1.0.0`

Variables de entorno recomendadas por script:

- DeepEval: `OPENAI_API_KEY` (o configuración de proveedor/modelo equivalente).
- Inspect: clave del proveedor + `INSPECT_EVAL_MODEL`.
- Azure SDK: `AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME`, `AZURE_API_VERSION`.

---

## 3. `01_deepeval_agent_eval.py` Recorrido Técnico Detallado

## 3.1 Propósito y Diseño

Este script demuestra ambos enfoques:

- evaluación black-box (`evaluate(...)`) para salidas finales.
- trazado a nivel de componente (`@observe`) para comportamiento interno del agente.

También incluye pruebas listas para CI al final del archivo, mostrando cómo bloquear merges según métricas de evaluación.

## 3.2 Imports Clave y su Rol

- `deepeval.evaluate`: ejecución por lotes sin pytest.
- `GEval`: constructor de métricas LLM-as-judge personalizadas.
- `ToolCorrectnessMetric`, `AnswerRelevancyMetric`, `PlanQualityMetric`, `PlanAdherenceMetric`: métricas integradas.
- `LLMTestCase`, `ToolCall`: esquema de datos de prueba.
- `observe`, `update_current_span`: trazado y asociación de test-case por span.
- `assert_test`: integración de aserciones con pytest.

## 3.2.1 Decoradores, Clases y Métodos que Debes Explicar

### Decorador: `@observe(...)`

Qué hace:

- envuelve una llamada de función en un span de trazabilidad evaluable por DeepEval.
- adjunta metadatos (por ejemplo, tipo de operación como `agent` o `tool`).

Por qué importa al presentar:

- te da visibilidad de pasos intermedios, no solo de la respuesta final.
- permite explicar en qué etapa exacta se degradó la calidad.

Cómo describir su comportamiento en ejecución:

- al iniciar la función decorada, se abre un span.
- dentro de la función, `update_current_span(...)` puede adjuntar el test-case.
- al retornar la función, el span se cierra y se aplican métricas.

### Método: `update_current_span(...)`

Qué hace:

- vincula un `LLMTestCase` al span activo actual.
- aporta contexto de evaluación para ese paso específico.

Punto didáctico:

- es el puente entre la ejecución de la lógica de negocio y la lógica de evaluación.

### Clase: `LLMTestCase`

Rol:

- contenedor canónico para un ítem de evaluación.
- contiene campos como `input`, `actual_output`, `expected_output` y opcionalmente datos de tool calls.

Enfoque didáctico:

- trátalo como un vector de prueba para comportamiento de LLM/agente.

### Clase: `GEval`

Rol:

- métrica configurable de tipo LLM-as-judge.
- combina nombre, criterios y parámetros de scoring en un objeto reutilizable.

Enfoque didáctico:

- aquí vive la rúbrica de dominio (por ejemplo: "¿la decisión de escalamiento cumple política?").

### Método: `evaluate(...)`

Rol:

- ejecuta una o varias métricas sobre uno o varios test cases.

Enfoque didáctico:

- úsalo cuando quieres corridas de evaluación desde script (fuera de pytest).

### Método: `assert_test(...)`

Rol:

- aserción compatible con pytest para resultados de métricas.

Enfoque didáctico:

- convierte expectativas de evaluación en gates de CI.

## 3.3 Sección por Sección

### Ejemplo 1: End-to-End Black-Box

Función: `example_1_end_to_end_evaluation()`

Qué muestra:

- construir una métrica judge personalizada (`GEval`) con criterios explícitos.
- combinar métricas personalizadas e integradas.
- evaluar múltiples `LLMTestCase` en una sola llamada.

Por qué importa:

- da una señal de regresión práctica para comportamiento visible por el usuario.
- no requiere instrumentar rutas internas de código.

### Ejemplo 2: Correctitud de Herramientas

Función: `example_2_tool_correctness()`

Qué muestra:

- `tools_called` vs `expected_tools` explícitos.
- validación de alineación agente-herramienta independiente de la calidad del texto.

Por qué importa:

- detecta fallos silenciosos donde la respuesta parece correcta, pero el uso de herramientas no lo es.

### Ejemplo 3: Trazado a Nivel de Componente

Función: `example_3_component_level_tracing()`

Qué muestra:

- trazado de una ruta orquestada (`travel_agent` -> razonamiento -> herramientas).
- aplicar métricas distintas en niveles distintos.
- poblar el test-case del span en runtime con `update_current_span(...)`.

Por qué importa:

- es ideal para depurar dónde falló: plan, herramientas o salida final.

### Ejemplo 4: Métrica Custom para Casos Límite

Función: `example_4_custom_geval_metric()`

Qué muestra:

- definir una rúbrica de calidad de dominio con `GEval`.
- validar comportamientos de clarificación ante solicitudes ambiguas.

Por qué importa:

- las métricas genéricas no suelen ser suficientes para comportamientos agénticos en producción.

### Sección 5: Pruebas de CI

Funciones:

- `test_agent_tool_selection()`
- `test_agent_response_quality()`

Qué muestra:

- `assert_test` como gate de CI.
- estructura determinista para pipeline.

Nota importante:

- estas pruebas dependen de proveedor/modelo y pueden fallar si no hay configuración correcta del modelo juez.

## 3.4 Cuándo Usar Este Patrón de Script

Usa este patrón cuando:

- quieres iteración local rápida con semántica de pytest.
- necesitas rúbricas custom y regresión developer-first.
- quieres evaluación black-box y white-box en el mismo flujo.

## 3.5 Guion de 2 Minutos (DeepEval)

"En este archivo, la idea clave es que la evaluación se trata como testing. Empiezo con `LLMTestCase`, que es el contrato de datos de lo que espero del agente. Luego combino métricas, incluyendo rúbricas custom con `GEval` y métricas integradas de herramientas o calidad.

El decorador más importante es `@observe`. Envuelve funciones en spans de trazabilidad para evaluar no solo el output final, sino también el comportamiento intermedio. Dentro de esos spans, `update_current_span(...)` vincula los datos del runtime al paso actual. Eso me da visibilidad de depuración cuando el agente acierta la respuesta pero con proceso incorrecto.

Por último, uso `evaluate(...)` para corridas desde script y `assert_test(...)` para gates de CI. Conceptualmente: este script es un workflow developer-first para regresión rápida y protección de merges." 

---

## 4. `02_inspect_ai_agent_eval.py` Recorrido Técnico Detallado

## 4.1 Propósito y Diseño

Este script demuestra composición de tareas en Inspect AI para evaluación de agentes.

Abstracción central:

- `Task = Dataset + Solver + Scorer`

Es útil para tareas reproducibles tipo benchmark y pipelines de solver flexibles.

## 4.2 Imports Clave y Roles

- `@task`, `Task`: registran tareas de evaluación ejecutables.
- `Sample`: fila de dataset.
- `generate`, `system_message`, `use_tools`: primitivas de pipeline de solver.
- `@tool`: wrappers async para herramientas personalizadas.
- scorers: `model_graded_fact`, `accuracy`, además de API de scorer custom.
- `react`: bucle agéntico ReAct incorporado.

## 4.2.1 Decoradores, Clases y Métodos que Debes Explicar

### Decorador: `@tool`

Qué hace:

- registra una función de Python como herramienta invocable en Inspect.
- espera que retornes una función async `execute(...)` invocada en runtime.

Por qué existe este patrón:

- separa la declaración de la herramienta de su implementación de ejecución.
- permite a Inspect exponer firmas/descripciones al modelo.

Tip para presentación:

- resalta que docstrings y type hints mejoran la calidad de uso de herramientas porque forman parte del contrato que ve el modelo.

### Decorador: `@task`

Qué hace:

- marca una función que retorna `Task(...)` como tarea de evaluación ejecutable.
- habilita direccionamiento CLI como `archivo.py@nombre_tarea`.

Tip para presentación:

- esta es la unidad principal de empaquetado de evaluación en Inspect.

### Decorador: `@scorer(metrics=[...])`

Qué hace:

- declara una función de scoring personalizada y conecta metadatos de agregación de métricas.
- en este script, `refusal_scorer` retorna `CORRECT` o `INCORRECT` con explicación.

Tip para presentación:

- aquí conviertes políticas de seguridad en criterios explícitos y auditables.

### Clase: `Task`

Rol:

- contenedor de alto nivel para `dataset`, `solver` y `scorer`.

Cómo explicarlo rápido:

- "Task es el contrato ejecutable: qué correr, cómo correrlo y cómo puntuarlo."

### Clase: `Sample`

Rol:

- una fila de dataset (`input` + expectativa `target`).

Tip para presentación:

- los targets pueden ser respuestas estrictas o hechos esperados más flexibles, según la estrategia de scoring.

### Métodos de solver: `system_message(...)`, `use_tools(...)`, `generate()`

Orden de ejecución:

1. `system_message(...)` define restricciones de comportamiento del modelo.
2. `use_tools(...)` adjunta interfaces de herramientas disponibles para el modelo.
3. `generate()` ejecuta la completion del modelo para el sample.

Enfoque didáctico:

- esta cadena explícita hace fácil inspeccionar y comparar orquestación entre corridas.

### Solver ReAct: `react(...)`

Rol:

- habilita ciclos iterativos de razonar/actuar con herramientas.
- soporta tareas más difíciles donde un solo turno no basta.

Nota de seguridad/operación:

- `message_limit` es un guardrail práctico para evitar loops descontrolados.

### Tipos de scoring: `Score`, `Target`, `CORRECT`, `INCORRECT`

Rol:

- contrato de salida estandarizado para scorers custom.

Tip para presentación:

- devolver un `explanation` es tan importante como la etiqueta, porque acelera depuración e iteración de modelo.

## 4.3 Sección por Sección

### Definiciones de Herramientas (`search_knowledge_base`, `calculate_shipping`, etc.)

Qué muestra:

- herramientas personalizadas como funciones async con firmas claras.
- datos mock deterministas para comportamiento reproducible.

Por qué importa:

- el comportamiento de herramientas queda explícito y estable para pruebas.

### Tarea 1: `customer_support_agent`

Qué muestra:

- tarea de soporte/QA estándar con uso de herramientas.
- scoring model-graded sobre intención/hechos objetivo.

### Tarea 2: `travel_planning_agent`

Qué muestra:

- composición de múltiples herramientas en una sola solicitud.
- requisitos de síntesis más ricos que un QA de un turno.

### Tarea 3: `react_agent_eval`

Qué muestra:

- bucle de agente estilo ReAct con guardrail `message_limit`.
- comportamiento más cercano a autonomía multi-paso.

### Tarea 4: `safety_evaluation` + `refusal_scorer`

Qué muestra:

- chequeos de comportamiento de política ante prompts dañinos.
- scorer custom con heurística explícita de rechazo y resultado binario.

## 4.4 Modelo de Ejecución

Ruta principal de ejecución por CLI:

```bash
inspect eval 02_inspect_ai_agent_eval.py
```

Puedes ejecutar todas las tareas o una específica:

```bash
inspect eval 02_inspect_ai_agent_eval.py@customer_support_agent
```

Inspect emite logs en `./logs/` y puedes visualizarlos con:

```bash
inspect view
```

## 4.5 Cuándo Usar Este Patrón de Script

Usa este patrón cuando:

- necesitas modelado fuerte de tareas de evaluación (datasets/solvers/scorers).
- quieres workflows tipo benchmark con logs detallados de ejecución.
- necesitas evaluar comportamiento de agente y herramientas con orquestación reproducible.

## 4.6 Guion de 2 Minutos (Inspect AI)

"Este archivo está organizado alrededor de la abstracción central de Inspect: `Task = Dataset + Solver + Scorer`. Un `Sample` aporta un caso input-target, el solver define cómo corre el modelo, y el scorer define cómo se juzga la calidad.

Los decoradores son clave. `@task` registra unidades ejecutables por CLI. `@tool` convierte funciones Python en herramientas invocables por el modelo, donde type hints y docstrings forman parte del contrato de herramienta. `@scorer` define scoring personalizado, que es como vuelvo explícitas políticas de seguridad, por ejemplo las reglas de rechazo.

Para el flujo de ejecución, leo la cadena del solver de arriba abajo: `system_message(...)`, `use_tools(...)`, luego `generate()`. Para casos más complejos, `react(...)` introduce ciclos iterativos de razonar/actuar. Este script se entiende mejor como un pipeline de benchmark reproducible con separación clara de datos, orquestación y scoring." 

---

## 5. `03_azure_ai_eval_agents.py` Recorrido Técnico Detallado

## 5.1 Propósito y Diseño

Este script demuestra métricas agénticas del Azure AI Evaluation SDK con ambos modos:

- invocaciones de evaluadores en corrida individual.
- evaluación batch con `evaluate(...)` sobre JSONL.

Evaluadores principales:

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`

## 5.2 Configuración

`AzureOpenAIModelConfiguration` se usa como objeto de configuración del modelo:

- `azure_endpoint`
- `api_key`
- `azure_deployment`
- `api_version`

Este script usa estas variables de entorno:

- `AZURE_ENDPOINT`
- `AZURE_API_KEY`
- `AZURE_DEPLOYMENT_NAME`
- `AZURE_API_VERSION`

## 5.2.1 Decoradores, Clases y Métodos que Debes Explicar

Este script está orientado a evaluadores y no depende de decoradores de Python.
El foco didáctico importante aquí es la invocación de evaluadores basada en clases.

### Clase: `AzureOpenAIModelConfiguration`

Rol:

- encapsula endpoint/deployment/autenticación del modelo.
- se pasa a los evaluadores para que el scoring use una configuración consistente.

Tip para presentación:

- explícalo como inyección de dependencia del modelo juez.

### Clases evaluadoras

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`

Patrón compartido en runtime:

- instanciar el evaluador con `model_config` (o settings explícitos).
- invocar el evaluador como función: `result = evaluator(query=..., response=...)`.

Enfoque didáctico:

- son objetos evaluadores invocables; cada uno retorna un diccionario estructurado con scores y campos de razón opcionales.

### Método: evaluador `__call__(...)`

Comportamiento práctico:

- valida el esquema de entrada.
- ejecuta la ruta de prompt/inferencia del evaluador.
- retorna salidas de métrica normalizadas.

Tip para presentación:

- por eso la calidad del input (sobre todo trazas de mensajes y IDs de tool calls) impacta directamente la confiabilidad.

### Función: `evaluate(...)` (modo batch)

Rol:

- ejecuta uno o varios evaluadores sobre un dataset JSONL.
- soporta `column_mapping` por evaluador para leer campos distintos.

Enfoque didáctico:

- es la ruta productiva para jobs nocturnos o de release candidate.

## 5.3 Notas Críticas de Esquema de Entrada

Según comportamiento actual del SDK y documentación:

- los tool calls deben incluir `tool_call_id` en ítems de tipo tool call.
- el formato de mensajes del agente debe seguir listas de mensajes estilo OpenAI.
- para confiabilidad de parsing en evaluadores, el `content` de usuario/asistente se representa como lista de ítems (`type: text/tool_call/tool_result`) en este script.

## 5.4 Sección por Sección

### Ejemplo 1: Resolución de Intención

Función: `example_1_intent_resolution()`

Qué muestra:

- casos claros positivos, negativos y de clarificación.
- interpretación de umbral pass/fail para alineación de intención.

### Ejemplo 2: Adherencia de Tarea

Función: `example_2_task_adherence()`

Qué muestra:

- el caso positivo incluye evidencia de tool call y tool result.
- el caso negativo permanece intencionalmente sub-especificado.
- se imprimen campos de razón para explicabilidad.

Detalle de implementación importante:

- en versiones actualmente instaladas del SDK, la salida de task adherence es binaria (`1.0/0.0` + razón), aunque documentación antigua menciona estilo Likert. Trátalo como comportamiento sensible a versión.

### Ejemplo 3: Precisión de Tool Calls

Función: `example_3_tool_call_accuracy()`

Qué muestra:

- arrays explícitos de `tool_definitions` y `tool_calls`.
- evaluación directa de calidad procedural del uso de herramientas.

### Ejemplo 4: Evaluación con Traza de Mensajes

Función: `example_4_agent_messages_format()`

Qué muestra:

- construcción de `query_messages` y `response_messages` amigables para evaluadores a partir de una traza.
- evaluación de intención y adherencia sobre conversación estructurada.

### Ejemplo 5: Evaluación Batch

Función: `example_5_batch_evaluation()`

Qué muestra:

- generación de input de evaluación en JSONL.
- ejecución de múltiples evaluadores en una sola llamada `evaluate(...)`.
- uso de `column_mapping` para distintas formas de entrada por evaluador.

Nota operacional:

- warnings como `Aggregated metrics for evaluator is not a dictionary...` pueden aparecer por internals batch del SDK y suelen ser no fatales cuando todas las filas completan.

### Ejemplo 6: Calidad + Seguridad Combinadas (calidad ejecutada, seguridad documentada)

Función: `example_6_quality_and_safety()`

Qué muestra:

- ejecución conjunta de evaluadores de calidad.
- impresión de campos de razón para intención/tarea.
- documentación de evaluadores de seguridad y prerequisitos.

Comportamiento actual del script:

- los evaluadores de seguridad no se ejecutan en esta función; el script documenta métricas de seguridad soportadas y requisito de Foundry.

## 5.5 Cuándo Usar Este Patrón de Script

Usa este patrón cuando:

- quieres acceso directo a APIs de evaluadores de Azure.
- necesitas métricas agénticas ligadas a comportamiento de herramientas y resultados de intención/tarea.
- quieres evaluación batch con integración opcional de Foundry.

## 5.6 Guion de 2 Minutos (Azure AI Evaluation SDK)

"Este script está impulsado por objetos evaluadores. En lugar de decoradores, instancio clases evaluadoras como `IntentResolutionEvaluator`, `TaskAdherenceEvaluator` y `ToolCallAccuracyEvaluator` usando `AzureOpenAIModelConfiguration`.

En runtime, cada evaluador es invocable, así que paso `query` y `response` (o trazas de mensajes) y recibo scores estructurados más campos de razón. El detalle de implementación más importante es la calidad del esquema: IDs de tool calls y estructura de mensajes deben ser consistentes o cae la confiabilidad del evaluador.

Para escalar, paso a `evaluate(...)` batch sobre JSONL y uso `column_mapping` por evaluador para alimentar los campos correctos a cada métrica. Este archivo es la ruta orientada a producción: contratos consistentes, salidas explicables y ejecución lista para lotes." 

---

## 6. Comparación Entre Scripts

- `01_deepeval_agent_eval.py`: ideal para pruebas estilo CI con rúbricas custom y trazado en workflows de desarrollo.
- `02_inspect_ai_agent_eval.py`: ideal para tareas de evaluación estructuradas y pipelines tipo benchmark.
- `03_azure_ai_eval_agents.py`: ideal para APIs nativas de evaluación en Azure y métricas agénticas de calidad.

Un workflow práctico es combinarlos:

1. Usar DeepEval en ciclos rápidos locales/unitarios.
2. Usar Inspect AI para suites por escenario/benchmark y logs ricos.
3. Usar evaluadores de Azure para seguimiento de calidad agéntica alineado a producción.

---

## 6.1 Cheat Sheet del Presentador: Cómo Explicar los Tres Paradigmas

Si necesitas una frase por script durante la charla:

- `01_deepeval_agent_eval.py`: "Trazado guiado por decoradores y aserciones métricas para ciclos CI developer-first."
- `02_inspect_ai_agent_eval.py`: "Objetos Task con composición explícita dataset/solver/scorer para benchmarking reproducible de agentes."
- `03_azure_ai_eval_agents.py`: "Invocaciones de evaluadores basadas en clases y pipelines batch para seguimiento de calidad agéntica en Azure."

Si necesitas una frase por estilo de programación:

- Estilo decorador: "El comportamiento se adjunta declarativamente a funciones (`@observe`, `@task`, `@tool`, `@scorer`)."
- Estilo objeto: "El comportamiento se adjunta a instancias de evaluadores e invocación de clases callables."
- Estilo pipeline: "El comportamiento se adjunta a pasos ordenados del solver y evaluadores batch con mappings."

---

## 7. Referencias

- DeepEval docs: https://deepeval.com/docs/getting-started?utm_source=GitHub
- DeepEval repo: https://github.com/confident-ai/deepeval
- Inspect docs: https://inspect.aisi.org.uk/
- Inspect repo: https://github.com/UKGovernmentBEIS/inspect_ai?tab=readme-ov-file
- Blog de métricas agénticas de Azure: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/evaluating-agentic-ai-systems-a-deep-dive-into-agentic-metrics/4403923
- Repo Azure AI Evaluation SDK: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation
- Docs Foundry classic (agent evaluate): https://learn.microsoft.com/en-us/azure/foundry-classic/how-to/develop/agent-evaluate-sdk
