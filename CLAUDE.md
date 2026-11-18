# antesdelos90-studio · instrucciones para Claude

Canal de táctica de fútbol **@antesdelos90** (YouTube y TikTok) de Miguel, entrenador de fútbol base en Málaga.
Todo en español de España. Miguel revisa y aprueba; tú propones, produces y mides.

## Rutina semanal (tarea programada de los lunes)
1. Lee `data/metrics.json`, `data/report.md`, `data/history.csv` y **`data/aprendizajes.md`**. Compara vídeos a la misma edad (columna "Vistas a 24 h"), % visto y suscriptores. Contrasta el experimento de la semana pasada con su resultado y apúntalo en `aprendizajes.md` (qué se probó, qué pasó, qué se mantiene). Elige **un solo cambio nuevo** que probar esta semana (gancho, duración, tema, hora, voz/sin voz…) y anótalo como experimento. Pide a Miguel en el mensaje final el dato "Lo vieron / Lo pasaron" de los vídeos de la semana (solo sale en YouTube Studio).
2. Decide el **formato según el tema**:
   - **Con la voz de Miguel** (1–2 por semana): sistemas completos, actualidad de equipos/entrenadores, opinión o historia — temas que ganan con explicación y criterio de entrenador. Guion conversacional de 60–75 s (150–190 palabras), nada de listas rígidas, gancho en la primera frase, cierre con pregunta y "sígueme".
   - **Sin voz** (el resto): micro-conceptos de 20–35 s (estructuras, movimientos, roles) que se entienden con animación y subtítulos.
   En total 5 vídeos a la semana, uno por día de martes a sábado.
3. Investiga en la web los temas: conceptos tácticos, sistemas, equipos de actualidad. Comprueba cada dato en fuentes abiertas y actuales (no de memoria): alineaciones, entrenadores, títulos, cifras.
4. Para cada vídeo crea `queue/<AAAA-MM-DD>-<tema>/spec.json` + `meta.json` (ver formato en `engine/render_spec.py` y el ejemplo `queue/2026-11-14-4231-estructura-226/`).
   - `meta.json`: `"status": "approved"`, `publish_at` en hora de Madrid (`+01:00` en invierno, `+02:00` en verano), uno por día de martes a sábado a las 13:30 o 19:30, título ≤ 100 caracteres terminado en `#shorts`, descripción con 3–5 hashtags, `sources` con las URLs usadas.
   - Renderiza una hoja de fotogramas de cada uno: `python engine/render_spec.py queue/<slug>/spec.json previews/<slug>.jpg --sheet 1 5 9 13 17 21 25 29` y **mírala** antes de seguir: nada tapado, textos legibles, movimientos con sentido.
   - `python pipeline/validate.py` debe pasar.
5. **Revisión independiente antes de publicar:** lanza un subagente que no haya visto tu trabajo para que revise cada vídeo (hoja de fotogramas + spec + fuentes) contra los criterios de abajo y compruebe cada dato en sus fuentes. Corrige todo lo que encuentre; si un dato no se sostiene, quítalo o descarta el vídeo.
6. Escribe el resumen de la semana en `data/semanas/<AAAA-MM-DD>.md` (conclusiones de métricas, 5 temas y por qué, fuentes, cambios tras la revisión) y haz commit **directamente en `main`**. Publicación 100 % automática: el workflow sube cada vídeo unas 30 h antes de su hora y YouTube lo publica a la hora programada.
7. **Vídeos con voz:** `meta.json` con `"voice": true`, `"status": "awaiting_voice"` y `publish_at` objetivo; `spec.json` con `"voice": true`, `"script"` (los párrafos tal cual los leerá), `"keywords"`, `"captions": "auto"`, `"end": "auto"` y los tiempos como frases del guion (`"@los laterales suben"`, ver `ejemplos/voz-442/spec.json`). Escribe también `guion.md` en su carpeta. La hoja de previsualización usa tiempos estimados. Envía a Miguel el guion completo en el mensaje final con este enlace para subir la grabación: `https://github.com/JotaEme29/antesdelos90-studio/upload/main/queue/<slug>` (archivo `voz.m4a`). Cuando la sube, el workflow transcribe, alinea, renderiza y programa solo (si su hora ya pasó, en el siguiente hueco a las 19:30).
8. **TikTok (manual, Miguel los programa en TikTok Studio desde el ordenador):** renderiza completos los vídeos sin voz de la semana (`python engine/render_spec.py queue/<slug>/spec.json build/<slug>.mp4`), revisa que duran lo previsto y envíaselos con SendUserFile. En el mensaje final, para cada uno: día y hora sugeridos (los mismos que en YouTube) y el texto para TikTok listo para copiar (gancho + 1–2 frases + pregunta, sin `#shorts`, con 4–5 hashtags tipo `#tacticadefutbol #futbolbase #entrenadordefutbol #sistemasdejuego` + el del sistema). Guarda ese texto también en `queue/<slug>/tiktok.txt`. Los vídeos con voz se renderizan en GitHub cuando Miguel sube la grabación y quedan para descargar en `https://github.com/JotaEme29/antesdelos90-studio/releases/tag/tiktok`; díselo junto al guion.
9. Si existe el archivo `PAUSA` en la raíz, no generes nada y avisa a Miguel. No toques los secretos.

## Cómo frena Miguel algo
- Un vídeo concreto: poner `"status": "draft"` en su `meta.json` antes de que se suba (se sube ~30 h antes de su hora). Si ya está subido, borrarlo o pasarlo a privado en YouTube Studio.
- Todo: crear un archivo `PAUSA` en la raíz del repositorio. Borrarlo para reanudar.

## Criterios de contenido (de Miguel)
- **Gancho en el primer segundo** (campo `hook` del spec, obligatorio): pregunta o idea polémica corta, 2 líneas, en el centro. En los vídeos con voz, la **primera frase del guion es esa pregunta** (nunca "El 3-5-2. Tres centrales…"). El 95 % de las vistas viene del feed de Shorts: si no engancha en 1 s, se pasa.
- Zona segura: nada importante en los ~220 px de arriba ni los ~420 de abajo ni en la columna derecha (ya lo respeta el motor).
- Equipos y entrenadores que se nombran → ficha `card` (nombre, entrenador y años, escudo genérico con colores del club). Nunca escudos oficiales ni fotos.
- El campo **siempre entero** a la vista; se mueve el equipo entero, también el rival cuando reacciona.
- Explicado paso a paso (subtítulos numerados o frases cortas con *clave* resaltada). Sin voz: 20–35 s. Con voz: 60–75 s.
- Nada de datos inventados ni estadísticas sin fuente. Si un dato no se puede verificar, no va.
- El sistema no decide si el extremo va por dentro o por fuera: laterales y extremos se compensan. No digas que un sistema es "difícil de entrenar".
- Ligado a la serie "Sistemas de juego" (kicker del tipo `4-2-3-1 · SISTEMAS DE JUEGO`).
- Cierre con pregunta para comentarios y `@antesdelos90`.
- Música solo de `music/` (Biblioteca de audio de YouTube).

## Comprobaciones técnicas
- Los workflows (`publish.yml`, `monitor.yml`) los lanza GitHub; para relanzar, un commit en `queue/` sirve.
- Estados de `meta.json`: `draft` → (`awaiting_voice` →) `approved` → `scheduled` → `published` / `failed` (con `error`).
