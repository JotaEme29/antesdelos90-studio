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
4. **Revisión independiente antes de publicar:** lanza un subagente que no haya visto tu trabajo para que revise cada vídeo (hoja de fotogramas + spec + fuentes) contra los criterios de abajo y compruebe cada dato en sus fuentes. Corrige todo lo que encuentre; si un dato no se sostiene, quítalo o descarta el vídeo.
5. Escribe el resumen de la semana en `data/semanas/<AAAA-MM-DD>.md` (conclusiones de métricas, 5 temas y por qué, fuentes, cambios tras la revisión) y haz commit **directamente en `main`**. Publicación 100 % automática: el workflow sube cada vídeo unas 30 h antes de su hora y YouTube lo publica a la hora programada.
6. Si existe el archivo `PAUSA` en la raíz, no generes nada y avisa a Miguel. No toques los secretos.

## Cómo frena Miguel algo
- Un vídeo concreto: poner `"status": "draft"` en su `meta.json` antes de que se suba (se sube ~30 h antes de su hora). Si ya está subido, borrarlo o pasarlo a privado en YouTube Studio.
- Todo: crear un archivo `PAUSA` en la raíz del repositorio. Borrarlo para reanudar.

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
