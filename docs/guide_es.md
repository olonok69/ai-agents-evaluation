# EVALUACIÓN DE AGENTES IA
## Técnicas, Herramientas y Frameworks

**Guía del Presentador — Presentación Técnica de 60 Minutos**

---

**Juan Salvador Huertas Romero**
Senior AI/ML Engineer

*Guía Práctica para 2025–2026*

---

## Resumen de la Sesión

Esta guía acompaña una presentación de 15 diapositivas diseñada para una audiencia técnica familiarizada con IA generativa, LLMs y arquitecturas de agentes. El objetivo no es introducir qué son los agentes, sino proporcionar un marco estructurado y accionable para evaluarlos — desde desarrollo hasta producción.

### Guías Técnicas Relacionadas

- Documentación técnica detallada de código (EN): `docs/technical_guide_en.md`
- Resumen técnico conceptual (ES): `docs/technical_guide_es.md`

### Distribución del Tiempo

| Tiempo | Sección | Slides | Duración |
|--------|---------|--------|----------|
| 0:00 | Apertura y por qué los evals de agentes son diferentes | 1–3 | 8 min |
| 0:08 | 7 Técnicas de Evaluación | 4–5 | 10 min |
| 0:18 | Métricas que Importan | 6 | 7 min |
| 0:25 | Benchmarks y Frameworks | 7–8 | 8 min |
| 0:33 | Herramientas de Producción | 9 | 5 min |
| 0:38 | Ejemplos de Código (DeepEval, Inspect AI, Azure) | 10–12 | 12 min |
| 0:50 | Mejores Prácticas y Conclusiones | 13–15 | 5 min |
| 0:55 | Preguntas y Respuestas | — | 5 min |

---

## ⏱ 0:00 – 0:08 — Apertura y Por Qué los Evals de Agentes Son Diferentes (Slides 1–3)

### Gancho Inicial

Comienza con un dato provocador: según el informe State of Agent Engineering 2026 de LangChain, el 57% de las organizaciones ya ejecutan agentes en producción, pero la calidad sigue siendo la barrera número uno — citada por el 32% de los equipos. Aún más llamativo: mientras que el 89% tiene observabilidad, solo el 52% ha implementado evaluaciones. Esta brecha entre «podemos ver lo que hacen nuestros agentes» y «podemos medir si lo hacen bien» es el problema central que aborda esta charla.

> 💡 **Nota para el presentador:** Abre con energía. Esta estadística suele generar asentimientos — la mayoría de la audiencia reconoce esta brecha en sus propias organizaciones. Haz una pausa después del 52% para que cale.

### Por Qué los Agentes Rompen los Evals Tradicionales

Los agentes fallan de formas fundamentalmente diferentes a las aplicaciones LLM estándar. Explica cuatro diferencias clave:

**No-determinismo:** La misma entrada produce secuencias de acciones diferentes en cada ejecución. Un agente de reserva de vuelos puede buscar primero por precio en una ejecución y por horario en otra — ambos llegando a resultados correctos por caminos distintos. Esto hace que la comparación simple entrada/salida sea insuficiente.

**Razonamiento multi-paso:** Necesitas evaluar la trayectoria completa (la cadena de razonamiento, llamadas a herramientas y decisiones), no solo la respuesta final. Un agente puede producir la respuesta correcta mediante un proceso defectuoso — y ese proceso defectuoso eventualmente causará fallos en tareas más complejas.

**Orquestación de herramientas:** Los agentes seleccionan herramientas, pasan argumentos, interpretan resultados y deciden qué hacer a continuación. Cada uno de estos pasos es un punto potencial de fallo. Un agente puede elegir la API correcta pero pasar parámetros incorrectos.

**Fallos en cascada:** Los errores se propagan. Una selección incorrecta de herramienta lleva a datos incorrectos, lo que lleva a un plan defectuoso, lo que lleva a una salida mala. Evaluar solo la salida oculta la causa raíz.

> 💡 **Nota para el presentador:** Usa la analogía: «La evaluación tradicional de LLM es como calificar un examen de matemáticas mirando solo la respuesta final. La evaluación de agentes es como calificar toda la demostración — ¿usaron los teoremas correctos, en el orden correcto, con razonamiento válido?»

---

## ⏱ 0:08 – 0:18 — 7 Técnicas de Evaluación (Slides 4–5)

Recorre cada técnica enfatizando cuándo usarla y sus limitaciones. No dediques el mismo tiempo a las siete — concéntrate en LLM-as-judge, evaluación de trayectoria y evaluación de uso de herramientas, que son las más específicas de agentes.

### 1. LLM-as-Judge (LLM como Juez)

El método dominante para evaluar salidas abiertas de agentes. Un LLM separado califica las respuestas del agente contra rúbricas estructuradas. La guía de Anthropic de enero 2026 recomienda aislar cada dimensión de evaluación en una llamada separada al juez — no pidas a un solo prompt que califique corrección, completitud y tono simultáneamente. La investigación de OpenAI muestra que los calificadores automáticos alcanzan aproximadamente 66% de acuerdo con expertos humanos, comparado con 71% de acuerdo entre humanos. Cercano pero no equivalente.

### 2. Evaluación Humana

Sigue siendo el estándar de oro para calibración. Hamel Husain recomienda un modelo de «dictador benevolente»: un experto de dominio que comprende profundamente a los usuarios toma las decisiones finales de calidad. Úsala para calibrar los jueces LLM, no como monitoreo continuo.

### 3. Benchmarks Automatizados

Proporcionan medición reproducible de capacidades. Menciona los benchmarks estáticos clave (SWE-bench para código, GAIA para razonamiento con herramientas, WebArena para automatización web) y destaca los benchmarks dinámicos emergentes: Bloom de Anthropic autogenera evaluaciones conductuales a partir de rasgos especificados.

### 4. Evaluación de Trayectoria

Evalúa la cadena completa de razonamiento y acciones. AgentEvals de LangChain ofrece evaluadores de coincidencia de trayectoria con cuatro modos: estricto, solo-llamadas-a-herramientas, subconjunto-ordenado y subconjunto-desordenado. Insight crítico de Anthropic: «Califica lo que el agente produjo, no el camino que tomó.»

### 5. Métricas de Completitud de Tarea

Dos métricas merecen atención. **pass@k** mide la probabilidad de que al menos 1 de k intentos tenga éxito — úsala cuando una buena respuesta es suficiente. **pass^k** mide la probabilidad de que TODOS los k intentos tengan éxito — úsala para fiabilidad en producción. Con 75% de éxito por intento y k=3: pass@k es 98% pero pass^k cae a solo 42%.

> 💡 **Nota para el presentador:** La distinción pass@k vs pass^k suele generar momentos 'ajá'. Desarróllalo: 75% suena genial, pero si necesitas fiabilidad, pass^k cuenta una historia muy diferente.

### 6. Evaluación de Conversación Multi-turno

Prueba coherencia, retención de contexto y seguimiento de objetivos a través de múltiples intercambios. El enfoque estándar usa un usuario simulado — un segundo LLM interpretando una persona de usuario.

### 7. Evaluación de Uso de Herramientas

Verifica selección correcta de herramientas, precisión de parámetros, eficiencia de llamadas, manejo de errores y corrección de secuencia. El Berkeley Function Calling Leaderboard (BFCL) proporciona medición estandarizada. Destaca el descubrimiento de Amazon: los esquemas de herramientas mal definidos causan fallos en cascada.

---

## ⏱ 0:18 – 0:25 — Métricas que Importan (Slide 6)

Presenta el stack de métricas en cuatro niveles. El mensaje clave: necesitas métricas en cada capa, no solo corrección.

### Nivel de Corrección (Medir Siempre)

La tasa de éxito de tareas es la métrica más importante. Los benchmarks de la industria muestran que los agentes de soporte de clase mundial alcanzan 85–90% de resolución en primer contacto. Combina con corrección de respuesta, fidelidad (proporción de afirmaciones respaldadas por contexto fuente) y tasa de alucinación.

### Nivel Específico de Agentes (Crítico para Debugging)

La precisión de llamadas a herramientas se divide en precisión de selección (¿herramienta correcta?) y corrección de argumentos (¿parámetros correctos?). El Azure AI Evaluation SDK trata estos como métricas agénticas primarias. La eficiencia de pasos (pasos óptimos / pasos reales) revela agentes que «giran en círculos» haciendo llamadas redundantes.

### Nivel de Rendimiento (Medir en Producción)

Registra latencia en P50, P95 y P99. Calcula coste por tarea como la suma de tokens de todas las llamadas LLM. La eficiencia de tokens (tareas completadas / tokens totales) revela oportunidades de optimización.

### Nivel de Seguridad (Crítico para Agentes de Cara al Usuario)

Hallazgo alarmante de octubre 2025: las 12 defensas publicadas contra jailbreak fueron eludidas en más del 90% de los casos bajo ataques adaptativos. Los ataques multi-turno alcanzaron tasas de éxito del 92% en ocho modelos de pesos abiertos. Esto convierte la resiliencia multi-turno en una métrica separada y esencial.

> 💡 **Nota para el presentador:** Las estadísticas de seguridad suelen sorprender incluso a ingenieros ML experimentados. Deja que cale — refuerza por qué la evaluación no es opcional, es infraestructura crítica.

---

## ⏱ 0:25 – 0:33 — Benchmarks y Frameworks (Slides 7–8)

Recorre la tabla de benchmarks brevemente. Luego profundiza en los cinco frameworks.

### Inspect AI (UK AI Security Institute)

El framework de evaluación open-source más completo. Su poder reside en el modelo de primitivas componibles: Dataset alimenta Task, que encadena Solvers (ingeniería de prompts, uso de herramientas, agentes ReAct), y las salidas son verificadas por Scorers. Ejecución sandboxed vía Docker o Kubernetes. Más de 100 evaluaciones pre-construidas ejecutables con un solo comando. Adoptado por Anthropic, DeepMind y otros labs de frontera. Licencia MIT.

### DeepEval (Confident AI)

Pensá en él como «Pytest para aplicaciones LLM». Su fortaleza es la ergonomía para desarrolladores: integración nativa con pytest hace que añadir puertas de evaluación al CI/CD sea trivial. Ofrece 50+ métricas incluyendo seis específicas para agentes: TaskCompletion, ToolCorrectness, ArgumentCorrectness, StepEfficiency, PlanQuality y PlanAdherence. El decorador `@observe` traza los internos del agente sin reescribir código.

### Azure AI Evaluation SDK (Microsoft)

Tres evaluadores agénticos diseñados a propósito: **IntentResolutionEvaluator** (¿entendió el agente el objetivo del usuario?), **TaskAdherenceEvaluator** (¿la respuesta satisfizo la solicitud?) y **ToolCallAccuracyEvaluator** (¿fueron correctas y eficientes las llamadas a herramientas?). Integración nativa con Azure AI Foundry Agent Service vía un converter. Ideal para equipos en el ecosistema Azure.

### Ragas y LangSmith

Ragas sigue siendo el estándar para evaluación RAG (Context Precision, Context Recall, Faithfulness) y se ha expandido con métricas de agentes. LangSmith proporciona la integración más estrecha para equipos LangChain/LangGraph con evaluadores de trayectoria y un Insights Agent que categoriza automáticamente patrones de comportamiento en producción.

---

## ⏱ 0:33 – 0:38 — Herramientas de Producción (Slide 9)

Recorre la tabla de herramientas. El mensaje clave es la convergencia en OpenTelemetry como capa estándar de instrumentación. Las GenAI Semantic Conventions (v1.37+) estandarizan esquemas de prompt, respuesta, tokens y llamadas a herramientas.

**LangSmith:** La más integrada para equipos LangChain. Maneja 1B+ trazas. Nivel gratuito: 5k trazas/mes.

**Arize Phoenix:** Mejor opción open-source. Auto-hosteable, nativa OTel con 50+ auto-instrumentaciones.

**Braintrust:** Loop de iteración CI/CD más rápido con GitHub Action dedicado.

**Galileo:** Latencia de evaluación sub-200ms usando SLMs propietarios Luna-2 a ~$0.02 por millón de tokens.

**Patronus AI:** Evaluación de grado investigativo con detector de alucinaciones Lynx.

> 💡 **Nota para el presentador:** El punto sobre OTel es la conclusión estratégica. Independientemente de qué herramientas elijas hoy, instrumentar con telemetría compatible con OTel previene el vendor lock-in. Esto resuena fuertemente con líderes de ingeniería.

---

## ⏱ 0:38 – 0:50 — Ejemplos de Código (Slides 10–12)

Esta es la sección más interactiva. Recorre cada ejemplo en pantalla, explicando los patrones clave en lugar de leer código línea por línea. Anima a la audiencia a usar los scripts Python proporcionados para experimentación práctica después de la charla.

### Ejemplo DeepEval (Slide 10)

Explica los patrones clave: el decorador `@observe` para trazado no intrusivo, cómo las métricas se adjuntan a componentes específicos (no solo a la salida final), y cómo `update_current_span` conecta los datos del test case con la ejecución trazada. El script (`01_deepeval_agent_eval.py`) contiene cinco ejemplos completos: evaluación black-box, ToolCorrectness, trazado a nivel de componente, métricas G-Eval personalizadas e integración con pytest para CI/CD.

### Ejemplo Inspect AI (Slide 11)

Enfatiza la arquitectura componible: Dataset proporciona casos de prueba, Solver define el pipeline de evaluación (system message, uso de herramientas, generate), y Scorer evalúa la salida. Muestra cómo `@tool` define herramientas personalizadas como funciones async de Python simples. El solver `react()` proporciona un bucle ReAct con lógica de reintento. El script (`02_inspect_ai_agent_eval.py`) incluye cuatro tareas: soporte al cliente, planificación de viajes, agente ReAct y evaluación de seguridad.

### Ejemplo Azure AI Evaluation SDK (Slide 12)

Recorre los tres evaluadores agénticos. IntentResolutionEvaluator y TaskAdherenceEvaluator devuelven puntuaciones Likert (1–5), mientras que ToolCallAccuracyEvaluator devuelve una tasa de aprobación (0–1). Muestra los dos formatos de entrada: strings simples (query + response) y trazas completas de mensajes estilo OpenAI. El script (`03_azure_ai_eval_agents.py`) contiene seis ejemplos cubriendo todos los evaluadores, formato de mensajes, evaluación por lotes y evaluación combinada calidad-seguridad.

> 💡 **Nota para el presentador:** No intentes ejecutar el código en vivo a menos que hayas probado el entorno. En su lugar, recorre los patrones y apunta a los scripts para estudio posterior. Ofrece compartir el enlace del repositorio al final.

---

## ⏱ 0:50 – 0:55 — Mejores Prácticas y Conclusiones (Slides 13–15)

### Mejores Prácticas a Enfatizar

**1. Comienza con 20–50 tareas de fallos reales.** La guía de Anthropic de enero 2026 enfatiza que los cambios tempranos tienen efectos grandes, por lo que tamaños de muestra pequeños son suficientes. Convierte verificaciones manuales en casos de prueba automatizados.

**2. Pirámide de evaluación de tres niveles.** Framework de Hamel Husain: Nivel 1 (aserciones basadas en código) se ejecuta en cada commit — barato, rápido, determinista. Nivel 2 (LLM-as-judge) se ejecuta con cadencia regular. Nivel 3 (evaluación humana) solo después de cambios significativos.

**3. Maneja el no-determinismo con múltiples intentos.** Ejecuta 3–10 intentos independientes por tarea. Usa entornos aislados — Anthropic descubrió que los agentes obtenían ventajas injustas examinando el historial de git de intentos anteriores.

**4. Lee las transcripciones.** La recomendación más fuerte de Anthropic. Los bugs de infraestructura frecuentemente se disfrazan de fallos de razonamiento — un solo bug de extracción movió el benchmark de un equipo del 50% al 73%.

**5. Integra evals en CI/CD.** Puertas de calidad con fallo automático ante caídas de puntuación. La integración pytest de DeepEval y el GitHub Action de Braintrust lo hacen práctico hoy.

**6. Construye suites de evaluación equilibradas.** Prueba tanto CUÁNDO los comportamientos DEBEN ocurrir como cuándo NO DEBEN. Las evaluaciones unilaterales crean optimización unilateral.

### Tres Conclusiones Clave

**Cambio 1 — De solo-salida a evaluación consciente de trayectoria:** Entender POR QUÉ fallan los agentes, no solo QUE fallan. Esto significa evaluar toda la cadena de razonamiento y acción.

**Cambio 2 — OpenTelemetry como estándar de convergencia:** Las GenAI Semantic Conventions previenen el vendor lock-in. Adopta instrumentación compatible con OTel ahora.

**Cambio 3 — Desarrollo dirigido por evaluaciones:** Escribe evals ANTES de escribir la lógica del agente. Las herramientas ya existen: Inspect AI para capacidad y seguridad, DeepEval para CI/CD, LangSmith o Arize Phoenix para observabilidad, y Azure AI Evaluation para integración enterprise.

> 💡 **Nota para el presentador:** Termina con el stack recomendado en la slide 14, luego pasa a Recursos (slide 15). Mantén el Q&A a 5 minutos. Si las preguntas son complejas, ofrece continuar offline.

---

## Apéndice: Preguntas Anticipadas

**P: ¿Con qué framework debería empezar?**
R: Si estás en el ecosistema Azure, comienza con Azure AI Evaluation SDK — es el camino más rápido. Para rigor open-source, Inspect AI. Para experiencia developer-first con CI/CD, DeepEval. Son complementarios, no competidores.

**P: ¿Cuántos evals necesito antes de ir a producción?**
R: Anthropic recomienda empezar con 20–50 tareas de fallos reales. No necesitas cobertura completa el día uno — empieza con los fallos que más cuestan y expande desde ahí.

**P: ¿Es LLM-as-judge suficientemente fiable?**
R: Con 66% de acuerdo con humanos (vs 71% inter-evaluador), está cerca pero no es equivalente. Úsalo para escala, calíbralo periódicamente con evaluación humana, y siempre lee las transcripciones para detectar sesgos sistemáticos.

**P: ¿Qué pasa con el coste?**
R: La evaluación tiene costes (llamadas al juez LLM), pero el coste de desplegar un agente defectuoso es mucho mayor. Luna-2 de Galileo funciona a ~$0.02 por millón de tokens. Empieza con aserciones basadas en código en CI y reserva jueces LLM costosos para staging.

**P: ¿Cómo manejamos el problema del no-determinismo?**
R: Ejecuta 3–10 intentos por tarea, usa entornos aislados y reporta pass@k para desarrollo y pass^k para fiabilidad en producción. Acepta que la evaluación de agentes es probabilística — el objetivo es confianza estadística, no certeza determinista.

---

**Entregables:** Presentación (Evaluating_AI_Agents.pptx) • 01_deepeval_agent_eval.py • 02_inspect_ai_agent_eval.py • 03_azure_ai_eval_agents.py • requirements.txt