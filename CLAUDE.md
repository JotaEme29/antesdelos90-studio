# antesdelos90-studio · instrucciones para Claude

Canal de táctica de fútbol **@antesdelos90** (YouTube y TikTok) de Miguel, entrenador de fútbol base en Málaga.
Todo en español de España. Miguel revisa y aprueba; tú propones, produces y mides.

## Rutina diaria (tarea programada, cada mañana)
Objetivo: un vídeo al día sobre **lo que está pasando en el fútbol**, en formato **cine** (`engine/cine.py`, ejemplo completo en `ejemplos/clasico-mourinho/render.py`). Cada vídeo debe ser mejor que el anterior: nada de plantillas repetidas.

1. **Métricas y aprendizaje.** Lee `data/metrics.json`, `data/report.md`, `data/history.csv` y `data/aprendizajes.md`. Compara a la misma edad (vistas a 24 h, % visto, subs). Una vez por semana (lunes) apunta en `aprendizajes.md` qué se probó, qué pasó y el **experimento** de la semana (un solo cambio). Corrige la línea editorial según lo que diga Miguel en `data/linea_editorial.md`.
2. **Tema del día (actualidad).** Busca en la web los partidos y noticias **de las últimas 24 h** (la actualidad caduca: se publica el mismo día, nunca al día siguiente ni encolado para otro día) (LaLiga, Premier, Champions, Serie A, Bundesliga, selección): un plan táctico que decidió un partido, un entrenador nuevo, un jugador que cambió de rol, una tendencia. Mira también qué publican los canales de táctica que funcionan (p. ej. @teactics, @tactics.mind, The Athletic, Coaches' Voice, Tifo) y adapta en español lo que funcione. Elige **un** tema con historia: conflicto, nombres reales, dato sorprendente. **No es un resumen de goles**: el vídeo explica tácticamente qué falló en un equipo y qué favoreció al otro (2–3 claves con su mecanismo en el campo); los goles van al final y rápidos, como consecuencia.
3. **Investigación con fuentes.** Comprueba cada dato (alineación, sistema, quién marcó a quién, minuto, resultado, cita, clasificación) en ≥2 fuentes abiertas y recientes. Si no se puede verificar, no va. Guarda las URLs en `meta.json` → `sources`.
4. **Guion visual por bloques** (40–55 s sin voz):
   - 0–2,5 s: **gancho** enorme (`bigtitle`) con afirmación que choque o pregunta, cámara baja en movimiento.
   - Contexto → mecanismo táctico (2–3 bloques) → la jugada clave (gol/ocasión con cámara lenta) → dato o cita → clasificación o consecuencia → pregunta que divida + `@antesdelos90`.
   - **Bloque «Antes de los 90» (obligatorio, 5–7 s, antes de la pregunta):** cómo se entrena esa clave **de forma integrada**: una tarea real (espacio, nº de jugadores, regla, qué se busca) donde lo físico, lo técnico, lo táctico y la decisión van juntos. Nunca "primero físico, luego técnico, luego táctico": el fútbol es uno solo (ver `data/linea_editorial.md`, 26-11-2026). Es propuesta de entrenador, no dato: va rotulada como tal y no necesita fuente.
   - **Cada 3–5 s cambia el plano** (`CAMK`): general, zoom a la zona, giro a la banda, cámara siguiendo el balón. Titular arriba que cambia por bloque, subtítulos que entran palabra a palabra, nombres de jugadores, fichas `lower_third`, `scoreboard`, `quote`, `table`, estelas, `flash`, efectos de sonido.
   - **Innova cada día**: añade al motor al menos una mejora visual nueva cada semana (p. ej. mapa de calor, comparativa en pantalla dividida, contador de datos, líneas de pase dibujándose, recorrido del balón en 3D) y úsala.
   - **Música**: rota entre los temas de `music/` (no repitas la del día anterior).
5. **Producción.** Crea `queue/<AAAA-MM-DD>-<tema>/render.py` (copia y adapta el ejemplo), `meta.json` (`"format": "cine"`, `"status": "approved"`, `publish_at` **ese mismo día**, lo antes posible (por defecto 14:00 hora de Madrid; si ya es tarde, ≥ 1 h después del push; nunca al día siguiente). Si ya hay otro vídeo ese día, sepáralos ≥ 1,5 h, título ≤ 100 caracteres con `#shorts`, descripción con 3–5 hashtags, `tags`, `sources`) y `tiktok.txt`. Haz hoja de fotogramas (`python queue/<slug>/render.py previews/<slug>.jpg --sheet 1 4 8 ...`) y **mírala**: nada tapado (zona segura), textos legibles, jugadores sin solaparse, movimientos con sentido. Renderiza el vídeo completo en `build/<slug>.mp4`, revisa duración y audio. `python pipeline/validate.py` debe pasar.
6. **Revisión independiente:** un subagente que no haya visto tu trabajo revisa la hoja, el guion y **cada dato contra sus fuentes**. Corrige todo; si algo no se sostiene, quítalo o cambia de tema.
7. **Publicar:** commit y push directo a `main` (el workflow sube y programa en YouTube). Envía a Miguel el vídeo (SendUserFile) con el texto de TikTok y la hora para programarlo.
8. **Con voz (1 por semana, lo revisa Miguel antes):** `meta.json` con `"voice": true`, `"status": "awaiting_voice"`; en `render.py` usa `cine.voice_clock(SCRIPT)` para sincronizar planos con frases (`V.at("frase")`) y `C.encode(..., voice=V.wav)`. Guion de 150–190 palabras, la **primera frase es el gancho**. Escribe `guion.md` y envía a Miguel el guion completo con el enlace `https://github.com/JotaEme29/antesdelos90-studio/upload/main/queue/<slug>` (archivo `voz.m4a`). Si hay arranques en falso en la grabación, córtalos.
9. Resumen breve del día en `data/semanas/<AAAA-MM-DD>.md`. Si existe `PAUSA` en la raíz, no generes nada y avisa a Miguel. No toques los secretos.

## Cómo frena Miguel algo
- Un vídeo concreto: poner `"status": "draft"` en su `meta.json` antes de que se suba (se sube ~30 h antes de su hora). Si ya está subido, borrarlo o pasarlo a privado en YouTube Studio.
- Todo: crear un archivo `PAUSA` en la raíz del repositorio. Borrarlo para reanudar.

## Criterios de contenido (de Miguel)
- **Gancho en el primer segundo** (campo `hook` del spec, obligatorio): pregunta o idea polémica corta, 2 líneas, en el centro. En los vídeos con voz, la **primera frase del guion es esa pregunta** (nunca "El 3-5-2. Tres centrales…"). El 95 % de las vistas viene del feed de Shorts: si no engancha en 1 s, se pasa.
- Zona segura: nada importante en los ~220 px de arriba ni los ~420 de abajo ni en la columna derecha (ya lo respeta el motor).
- Equipos, jugadores y entrenadores: por su nombre en texto y con los colores del club. Nunca escudos oficiales ni fotos.
- Planos variados (zoom, giros, cámara baja), pero en cada bloque se ve el contexto: se mueve el equipo entero, también el rival cuando reacciona.
- Explicado paso a paso con frases cortas y *clave* resaltada. Sin voz: 40–55 s. Con voz: 60–75 s.
- Nada de datos inventados ni estadísticas sin fuente. Si un dato no se puede verificar, no va.
- El sistema no decide si el extremo va por dentro o por fuera: laterales y extremos se compensan. No digas que un sistema es "difícil de entrenar".
- Temas de actualidad con nombres reales; los sistemas se explican a través de equipos y partidos concretos.
- El nombre del canal tiene doble sentido: lo que decide un partido **y** cómo se prepara y se entrena hoy antes de los 90'. El fútbol se entiende y se entrena como un todo (físico, técnico, táctico y psicológico a la vez), nunca por partes.
- Cierre con pregunta para comentarios y `@antesdelos90`.
- Música solo de `music/` (Biblioteca de audio de YouTube).

## Comprobaciones técnicas
- Los workflows (`publish.yml`, `monitor.yml`) los lanza GitHub; para relanzar, un commit en `queue/` sirve.
- Estados de `meta.json`: `draft` → (`awaiting_voice` →) `approved` → `scheduled` → `published` / `failed` (con `error`).
