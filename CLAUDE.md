# antesdelos90-studio · instrucciones para Claude

Canal de táctica de fútbol **@antesdelos90** (YouTube y TikTok) de Miguel, entrenador de fútbol base en Málaga.
Todo en español de España. Miguel revisa y aprueba; tú propones, produces y mides.

## Rutina diaria (tarea programada, cada mañana) · formato PIZARRA con la voz de Miguel (desde el 27-11-2026)
Objetivo: un vídeo al día sobre **lo que está pasando en el fútbol**, explicado como lo haría un entrenador: **una sola idea**, la voz de Miguel y una pizarra limpia que se entiende a la primera. Plantilla: `ejemplos/pizarra-celta/render.py` (motor `engine/cine.py`, modo pizarra v3.9). Investigación que lo justifica: doc «@antesdelos90 · Qué funciona en otros idiomas y plan de mejora» (27-11-2026) y `data/linea_editorial.md`.

1. **Métricas y aprendizaje.** Lee `data/metrics.json`, `data/report.md`, `data/history.csv` y `data/aprendizajes.md`. Compara a la misma edad (vistas a 24 h, % que se queda a ver, % visto, subs) **contra nuestra propia media**. Los lunes apunta en `aprendizajes.md` qué se probó, qué pasó y el **experimento** de la semana (un solo cambio). Aplica lo último de `data/linea_editorial.md`.
2. **Tema del día (actualidad, últimas 24 h).** Prioridad: LaLiga y nombres grandes (Madrid, Barça, Atleti, Málaga y lo que más se comenta en España); luego Champions, Premier, selección. Un tema con historia (conflicto, nombre propio, dato sorprendente) que se pueda contar con **una idea**. La actualidad caduca: se publica el mismo día.
3. **Formato del día** (rotan; ver el doc): 1) **De la tele al campo** (lo que pasó + cómo se entrena; el principal, tras cada jornada) · 2) **¿Qué es…? / ¿Por qué…?** (un concepto con el partido como ejemplo) · 3) **Así jugará el X de [entrenador nuevo]** (el día del cambio) · 4) **Píldora del míster n.º X** (problema real de un equipo de base y su tarea). Ocasionales: «Mismo rival, dos planes», «Un rol, tres versiones».
4. **Investigación con fuentes.** Cada dato (resultado, minuto, sistema, cita, estadística) en ≥2 fuentes abiertas y recientes; si no, no va. URLs en `meta.json` → `sources`.
5. **Guion de voz (80–110 palabras ≈ 25–40 s).** La **primera frase es el gancho**: una pregunta o idea que choque, con nombre propio. Frases cortas, de entrenador, en español de España. Una idea, su mecanismo en el campo (qué hace uno, qué deja al otro) y **cómo se entrena** de forma integrada (tarea real: espacio, jugadores, regla, qué se busca; físico, técnico, táctico y decisión a la vez). Cierra con una pregunta que divida. Sin datos de relleno.
6. **Producción (formato pizarra).** Copia la plantilla a `queue/<AAAA-MM-DD>-<tema>/render.py` y adapta SCRIPT, posiciones y dibujos. Reglas:
   - Plano cenital limpio que cambia poco (**cada 6–8 s**); como mucho **un momento en 3D**.
   - **Solo en color los 4–6 jugadores que cuentan** en cada momento; el resto en gris. Nombres en 2 como mucho.
   - **Una frase en pantalla cada vez** (la que dice la voz, `C.caption`), una línea, ≥ 2 s. Arriba, fija, la pregunta del vídeo (`C.question_top`).
   - **Una flecha/dibujo cada vez.** Nada de temblores, chispas en cadena, fichas y marcador a la vez.
   - Cierre: bloque «Antes de los 90» (`C.drillboard`, rotulado «Propuesta de entrenador») + pregunta + `@antesdelos90`.
   - **Música**: de `music/mixkit/` (Mixkit, licencia libre en cualquier red social), baja bajo la voz; no repitas ninguna de los 5 vídeos anteriores (`MUSIC=` al renderizar, y anótala en `meta.json` → `music`).
   - Cada semana, al menos **una mejora visual** al motor que sirva a la claridad (no más elementos).
   `meta.json`: `"format": "cine"`, `"voice": true`, `"status": "awaiting_voice"`, `publish_at` **ese mismo día** (14:00 Madrid por defecto; si ya es tarde, ≥ 1 h después; separado ≥ 1,5 h de otro vídeo del día), título ≤ 100 caracteres con `#shorts`, 3–5 hashtags, `tags`, `sources`. Escribe `guion.md` y `tiktok.txt`.
   Haz la hoja (`python queue/<slug>/render.py previews/<slug>.jpg --sheet ...`) y **mírala** (zona segura, legible, sin amontonar) y una **muestra** con tiempos estimados en `build/<slug>-muestra.mp4`. `python pipeline/validate.py` debe pasar.
7. **Revisión independiente:** un subagente que no haya visto tu trabajo revisa la hoja, el guion y **cada dato contra sus fuentes**. Corrige; si algo no se sostiene, fuera.
8. **Publicar:** commit y push a `main`. Envía a Miguel (SendUserFile la muestra + SendUserMessage) el **guion completo**, el enlace `https://github.com/JotaEme29/antesdelos90-studio/upload/main/queue/<slug>` para subir `voz.m4a` (30 s con el móvil) y el texto de TikTok. Cuando llega la voz, el workflow la limpia, la transcribe, sincroniza los planos con `V.at("frase")`, renderiza y lo programa **ese mismo día** (≥ 75 min después, separado 1,5 h). Si hay arranques en falso en la grabación, córtalos. Si al día siguiente no llegó la voz, pasa ese vídeo a `draft` (la actualidad ya caducó).
9. Resumen breve del día en `data/semanas/<AAAA-MM-DD>.md`. Si existe `PAUSA` en la raíz, no generes nada y avisa a Miguel. No toques los secretos.

## Cómo frena Miguel algo
- Un vídeo concreto: poner `"status": "draft"` en su `meta.json` antes de que se suba (se sube ~30 h antes de su hora). Si ya está subido, borrarlo o pasarlo a privado en YouTube Studio.
- Todo: crear un archivo `PAUSA` en la raíz del repositorio. Borrarlo para reanudar.

## Criterios de contenido (de Miguel)
- **Gancho en el primer segundo** (campo `hook` del spec, obligatorio): pregunta o idea polémica corta, 2 líneas, en el centro. En los vídeos con voz, la **primera frase del guion es esa pregunta** (nunca "El 3-5-2. Tres centrales…"). El 95 % de las vistas viene del feed de Shorts: si no engancha en 1 s, se pasa.
- Zona segura: nada importante en los ~220 px de arriba ni los ~420 de abajo ni en la columna derecha (ya lo respeta el motor).
- Equipos, jugadores y entrenadores: por su nombre en texto y con los colores del club. Nunca escudos oficiales ni fotos.
- Plano limpio y estable; en cada momento se ve el contexto (el equipo entero se mueve, también el rival), pero en color solo lo que cuenta la voz.
- Explicado paso a paso con frases cortas y *clave* resaltada. **Una idea por vídeo**, con voz: 25–40 s (la duración la pide la idea).
- Nada de datos inventados ni estadísticas sin fuente. Si un dato no se puede verificar, no va.
- El sistema no decide si el extremo va por dentro o por fuera: laterales y extremos se compensan. No digas que un sistema es "difícil de entrenar".
- Temas de actualidad con nombres reales; los sistemas se explican a través de equipos y partidos concretos.
- El nombre del canal tiene doble sentido: lo que decide un partido **y** cómo se prepara y se entrena hoy antes de los 90'. El fútbol se entiende y se entrena como un todo (físico, técnico, táctico y psicológico a la vez), nunca por partes.
- Cierre con pregunta para comentarios y `@antesdelos90`.
- Música solo de `music/` (temas de Mixkit en `music/mixkit/`, licencia en `music/mixkit/CREDITOS.md`; los 4 antiguos de la Biblioteca de YouTube).

## Comprobaciones técnicas
- Los workflows (`publish.yml`, `monitor.yml`) los lanza GitHub; para relanzar, un commit en `queue/` sirve.
- Estados de `meta.json`: `draft` → (`awaiting_voice` →) `approved` → `scheduled` → `published` / `failed` (con `error`).
