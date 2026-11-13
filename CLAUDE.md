# antesdelos90-studio · instrucciones para Claude

Canal de táctica de fútbol **@antesdelos90** (YouTube y TikTok) de Miguel, entrenador de fútbol base en Málaga.
Todo en español de España. Miguel revisa y aprueba; tú propones, produces y mides.

## Rutina semanal (tarea programada de los lunes)
1. Lee `data/metrics.json` y `data/report.md` (si existen): qué vídeos tienen más vistas, % visto y suscriptores ganados. Saca 2–3 conclusiones concretas.
2. Investiga en la web 5 temas para la semana: conceptos tácticos, sistemas, equipos de actualidad. Comprueba cada dato en fuentes abiertas y actuales (no de memoria): alineaciones, entrenadores, títulos, cifras.
3. Para cada vídeo crea `queue/<AAAA-MM-DD>-<tema>/spec.json` + `meta.json` (ver formato en `engine/render_spec.py` y el ejemplo `queue/2026-11-14-4231-estructura-226/`).
   - `meta.json`: `"status": "approved"`, `publish_at` en hora de Madrid (`+01:00` en invierno, `+02:00` en verano), uno por día de martes a sábado a las 13:30 o 19:30, título ≤ 100 caracteres terminado en `#shorts`, descripción con 3–5 hashtags, `sources` con las URLs usadas.
   - Renderiza una hoja de fotogramas de cada uno: `python engine/render_spec.py queue/<slug>/spec.json previews/<slug>.jpg --sheet 1 5 9 13 17 21 25 29` y **mírala** antes de seguir: nada tapado, textos legibles, movimientos con sentido.
   - `python pipeline/validate.py` debe pasar.
4. Abre un Pull Request (rama `semana-<AAAA-MM-DD>`) con los 5 vídeos, las hojas de `previews/` y un resumen: conclusiones de las métricas, temas elegidos y por qué, fuentes. **Hacer merge = Miguel aprueba**; el workflow publica solo lo que llega a `main`.
5. No publiques nada sin PR. No toques los secretos.

## Criterios de contenido (de Miguel)
- El campo **siempre entero** a la vista; se mueve el equipo entero, también el rival cuando reacciona.
- Explicado paso a paso (subtítulos numerados o frases cortas con *clave* resaltada). Vídeos de 20–35 s.
- Nada de datos inventados ni estadísticas sin fuente. Si un dato no se puede verificar, no va.
- El sistema no decide si el extremo va por dentro o por fuera: laterales y extremos se compensan. No digas que un sistema es "difícil de entrenar".
- Ligado a la serie "Sistemas de juego" (kicker del tipo `4-2-3-1 · SISTEMAS DE JUEGO`).
- Cierre con pregunta para comentarios y `@antesdelos90`.
- Música solo de `music/` (Biblioteca de audio de YouTube).

## Comprobaciones técnicas
- Los workflows (`publish.yml`, `monitor.yml`) los lanza GitHub; para relanzar, un commit en `queue/` sirve.
- Estados de `meta.json`: `draft` → `approved` → `scheduled` → `published` / `failed` (con `error`).
