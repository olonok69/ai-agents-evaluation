# Evaluación de Agentes de IA: DeepEval, Inspect AI y Azure AI Evaluation SDK

Repositorio profesional y práctico para evaluar agentes de IA con tres ecosistemas complementarios:

- `DeepEval` para evaluación test-first y orientada a CI
- `Inspect AI` para pipelines estructurados por tarea (`Dataset -> Solver -> Scorer`)
- `Azure AI Evaluation SDK` para métricas agénticas nativas de Azure y evaluación por lotes

Este repositorio está pensado para workshops, presentaciones técnicas y experimentación práctica con patrones reales de evaluación.

## Tabla de Contenidos

1. [Objetivos del Proyecto](#objetivos-del-proyecto)
2. [Qué Aprenderás](#qué-aprenderás)
3. [Estructura del Repositorio](#estructura-del-repositorio)
4. [Prerrequisitos](#prerrequisitos)
5. [Instalación](#instalación)
6. [Configuración de Entorno](#configuración-de-entorno)
7. [Cómo Ejecutar](#cómo-ejecutar)
8. [Resumen por Script](#resumen-por-script)
9. [Salidas y Logs](#salidas-y-logs)
10. [Documentación](#documentación)
11. [Resolución de Problemas](#resolución-de-problemas)
12. [Workflow Recomendado](#workflow-recomendado)

## Objetivos del Proyecto

El proyecto demuestra un enfoque multi-framework y práctico para evaluación de agentes:

- validar respuestas finales y comportamiento intermedio
- evaluar calidad de uso de herramientas y adherencia a tareas de usuario
- probar comportamiento de seguridad con criterios explícitos
- ejecutar evaluaciones unitarias y a escala de dataset (batch)
- preparar patrones de evaluación aptos para CI/CD y presentaciones técnicas

## Qué Aprenderás

Al recorrer los scripts, aprenderás a:

- definir test cases reutilizables y métricas custom de tipo judge
- instrumentar trazas a nivel de componente (`@observe`) para análisis white-box
- construir tareas Inspect AI con decoradores (`@task`, `@tool`, `@scorer`)
- evaluar conversaciones agénticas con trazas de mensajes estilo OpenAI
- ejecutar evaluadores Azure para intención, adherencia y precisión de tool calls
- escalar evaluaciones usando JSONL y `column_mapping` por evaluador

## Estructura del Repositorio

```text
.
|-- 01_deepeval_agent_eval.py
|-- 02_inspect_ai_agent_eval.py
|-- 03_azure_ai_eval_agents.py
|-- requirements.txt
|-- test_deepeval_agent_eval.py
|-- docs/
|   |-- guide_en.md
|   |-- guide_es.md
|   |-- technical_guide_en.md
|   `-- technical_guide_es.md
|-- logs/
`-- archive/
```

Notas:

- `logs/` almacena resultados de Inspect AI (`.eval`) para revisarlos con `inspect view`.
- `archive/` contiene scripts exploratorios antiguos conservados como referencia.

## Prerrequisitos

- Python `3.10+` recomendado
- acceso a proveedores de modelo según el script
- credenciales API según el framework que ejecutes

## Instalación

### Opción A: Entorno virtual (recomendado)

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Bash (macOS/Linux):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Opción B: Entorno existente

```bash
pip install -r requirements.txt
```

## Configuración de Entorno

Crea un archivo `.env` en la raíz del repositorio para ejecutar los ejemplos de Azure.

```env
# Azure AI Evaluation SDK
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_KEY=your-azure-openai-key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-12-01-preview
```

Variables adicionales:

- DeepEval: `OPENAI_API_KEY` (o configuración equivalente de proveedor)
- Inspect AI: `INSPECT_EVAL_MODEL` (ejemplo: `openai/gpt-4o`)

## Cómo Ejecutar

### 1) Ejemplos DeepEval

```bash
python 01_deepeval_agent_eval.py
```

Ejecución estilo CI:

```bash
deepeval test run 01_deepeval_agent_eval.py
```

### 2) Tareas Inspect AI

Ejecutar todas las tareas:

```bash
inspect eval 02_inspect_ai_agent_eval.py
```

Ejecutar una tarea específica:

```bash
inspect eval 02_inspect_ai_agent_eval.py@customer_support_agent
inspect eval 02_inspect_ai_agent_eval.py@travel_planning_agent
inspect eval 02_inspect_ai_agent_eval.py@react_agent_eval
inspect eval 02_inspect_ai_agent_eval.py@safety_evaluation
```

Ver resultados en interfaz web:

```bash
inspect view
```

### 3) Ejemplos Azure AI Evaluation SDK

```bash
python 03_azure_ai_eval_agents.py
```

Si `AZURE_API_KEY` no está configurada, el script muestra guía de setup y omite llamadas en vivo.

## Resumen por Script

### `01_deepeval_agent_eval.py`

Secciones principales:

- evaluación end-to-end black-box con `GEval` y métricas integradas
- validación de correctitud de herramientas (`tools_called` vs `expected_tools`)
- trazado a nivel de componente con `@observe` y `update_current_span(...)`
- métrica custom para casos límite
- pruebas compatibles con pytest mediante `assert_test(...)`

Ideal para:

- iteración rápida de desarrollo
- regresión en CI/CD
- combinar evaluación black-box y white-box

### `02_inspect_ai_agent_eval.py`

Secciones principales:

- herramientas custom con `@tool`
- tareas ejecutables con `@task`
- scorer de seguridad custom con `@scorer(metrics=[accuracy()])`
- cobertura multi-tarea (soporte, viajes, ReAct, seguridad)

Ideal para:

- workflows de evaluación estructurados tipo benchmark
- composición rica de tareas y ejecución reproducible
- análisis basado en logs con el visor de Inspect

### `03_azure_ai_eval_agents.py`

Secciones principales:

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`
- entrada con trazas de mensajes estilo OpenAI
- evaluación batch con `evaluate(...)` sobre JSONL
- sección de calidad + seguridad

Ideal para:

- pipelines de evaluación nativos en Azure
- métricas agénticas conectadas a despliegues productivos
- scoring por lotes con `column_mapping` por evaluador

## Salidas y Logs

- Inspect AI escribe artefactos de ejecución en `logs/`.
- El ejemplo batch de Azure escribe JSONL temporal en el directorio temporal del sistema y lo elimina al terminar.
- DeepEval imprime resultados por consola y se integra con flujos pytest/deepeval test.

## Documentación

La documentación de presentación y detalle técnico está en `docs/`:

- `docs/guide_en.md`: guía del presentador (EN)
- `docs/guide_es.md`: guía del presentador (ES)
- `docs/technical_guide_en.md`: walkthrough técnico detallado (EN)
- `docs/technical_guide_es.md`: walkthrough técnico detallado (ES)

## Resolución de Problemas

### Problemas en DeepEval

- verifica `OPENAI_API_KEY` (o proveedor configurado)
- algunas métricas dependen del modelo juez y pueden variar levemente entre corridas

### Problemas en Inspect AI

- define `INSPECT_EVAL_MODEL` o usa `--model`
- confirma credenciales del proveedor para el backend seleccionado
- usa `inspect view` tras ejecutar evaluaciones para revisar trazas

### Problemas en Azure AI Evaluation SDK

- valida `.env` (`AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME`, `AZURE_API_VERSION`)
- usa un deployment compatible con chat (`gpt-4o`, `gpt-4.1-mini`, etc.)
- asegura `tool_call_id` en los mensajes de tipo tool call cuando aplique
- considera que `TaskAdherenceEvaluator` puede variar según versión del SDK (en este repo se observó salida binaria)

## Workflow Recomendado

1. Comienza con `01_deepeval_agent_eval.py` para chequeos rápidos locales.
2. Continúa con `02_inspect_ai_agent_eval.py` para validar comportamiento multi-paso más complejo.
3. Ejecuta `03_azure_ai_eval_agents.py` para métricas agénticas alineadas a Azure y evaluación batch.
4. Usa `docs/technical_guide_en.md` o `docs/technical_guide_es.md` como referencia para explicación técnica.

---

Para workshops y presentaciones técnicas, usa las guías técnicas como referencia a nivel script y las guías del presentador para la narrativa de diapositivas.
