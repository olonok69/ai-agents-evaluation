# Checklist de Integracion de Evaluacion para Agente Real (ES)

Usa este checklist antes de promover cambios del agente a staging/produccion.

## 1) Preparacion de Captura de Datos

- [ ] Cada ejecucion del agente captura `run_id`, `timestamp`, `input`, `output`.
- [ ] Se capturan trazas de herramientas con `name`, `arguments`, `result`.
- [ ] Los tool calls incluyen `tool_call_id` estable cuando aplique.
- [ ] Se captura metadata de modelo/deployment (modelo, version, entorno).
- [ ] Se captura metadata de latencia y tokens/costo para analisis operativo.

## 2) Esquema Canonico de Trazas

- [ ] Existe un esquema JSON normalizado, definido y versionado.
- [ ] Se soportan etiquetas opcionales: `expected_output`, `expected_tools`.
- [ ] Existe validacion de esquema (JSON Schema, pydantic o equivalente).
- [ ] Campos faltantes/invalidos se registran con errores explicitos.

## 3) Adaptadores por Framework

- [ ] Existe adaptador: traza -> DeepEval `LLMTestCase`.
- [ ] Existe adaptador: traza -> Inspect `Sample` / input de tarea.
- [ ] Existe adaptador: traza -> Azure `query_messages` / `response_messages`.
- [ ] El adaptador de Azure preserva estructura de mensajes y consistencia de `tool_call_id`.
- [ ] La exportacion batch a JSONL es determinista y reproducible.

## 4) Integracion DeepEval

- [ ] Metricas core definidas (por ejemplo `GEval`, `AnswerRelevancyMetric`, `ToolCorrectnessMetric`).
- [ ] Umbrales definidos y documentados por metrica.
- [ ] Comando CI conectado (por ejemplo `deepeval test run ...`).
- [ ] Tests inestables identificados y tratados con reruns o rubricas mas precisas.

## 5) Integracion Inspect AI

- [ ] Los limites de tareas son explicitos (`@task` por familia de escenarios).
- [ ] El dataset refleja intenciones reales y modos de fallo.
- [ ] Las herramientas son productivas o mocks claramente definidos.
- [ ] Los scorers custom retornan etiqueta y explicacion.
- [ ] Los logs se revisan con `inspect view` en cada ciclo de evaluacion.

## 6) Integracion Azure AI Evaluation SDK

- [ ] `AzureOpenAIModelConfiguration` usa endpoint, key, deployment y API version correctos.
- [ ] `IntentResolutionEvaluator`, `TaskAdherenceEvaluator` y `ToolCallAccuracyEvaluator` estan mapeados a inputs correctos.
- [ ] Batch `evaluate(...)` usa `column_mapping` por evaluador correctamente.
- [ ] Rutas de warning conocidas del SDK estan documentadas para el equipo.
- [ ] Comportamientos sensibles a version del evaluador se registran en release notes.

## 7) Cobertura de Calidad y Seguridad

- [ ] Existen casos positivos y negativos.
- [ ] Se incluyen escenarios de seguridad (prompt injection, bypass de politicas, solicitudes daninas).
- [ ] El comportamiento de rechazo se prueba con criterios de politica explicitos.
- [ ] Se agenda revision humana para calibrar jueces automaticos.

## 8) CI/CD y Puertas de Release

- [ ] Metricas baseline almacenadas y versionadas.
- [ ] Umbrales de regresion definidos por metrica.
- [ ] El pipeline falla ante regresiones criticas.
- [ ] Artefactos de evaluacion archivados por build/release.
- [ ] Criterios de rollback documentados.

## 9) Operacion y Monitoreo

- [ ] Corridas de evaluacion nocturnas o programadas configuradas.
- [ ] Dashboard de tendencias monitorea deriva de metricas.
- [ ] Alertas configuradas para caidas relevantes de score.
- [ ] Costo y latencia monitoreados junto con metricas de calidad.

## 10) Decision Final de Go-Live

- [ ] Ninguna metrica critica por debajo del umbral de release.
- [ ] Ningun hallazgo bloqueante de seguridad sin resolver.
- [ ] Ultima calibracion humana aprobada.
- [ ] Sign-off del responsable de release registrado.

---

## Set Minimo de Lanzamiento (si necesitas empezar simple)

1. Capturar trazas normalizadas en cada ejecucion.
2. Ejecutar DeepEval + metricas Azure de intencion/tarea/herramientas cada noche.
3. Agregar una suite Inspect para los 10 journeys principales.
4. Bloquear releases con 2-3 metricas criticas.
5. Revisar semanalmente trazas fallidas con ingenieria + producto.
