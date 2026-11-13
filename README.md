# antesdelos90-studio

Fábrica de vídeos tácticos de **@antesdelos90**: guion → animación → YouTube, con revisión de Miguel.

## Cómo funciona
1. **Producción (automática, cada lunes).** Claude mira las estadísticas, investiga, crea 5 vídeos en `queue/` con su hoja de fotogramas en `previews/`, los hace revisar por un segundo agente y los sube a `main` con un resumen en `data/semanas/`.
2. **Freno (opcional, Miguel).** Para parar un vídeo: `"status": "draft"` en su `meta.json` antes de que se suba (~30 h antes de su hora). Para parar todo: crea un archivo `PAUSA` en la raíz.
3. **Publicación (automática).** `publish.yml` corre dos veces al día: valida, renderiza y sube los vídeos aprobados que se publican en las próximas 30 h, como privados programados (`publish_at`). YouTube los hace públicos a esa hora.
4. **Vigilancia (automática, cada 6 h).** `monitor.yml` comprueba que cada vídeo se procesó y se publicó, y descarga las estadísticas a `data/report.md`. Si algo falla, GitHub te manda un email.
5. **Mejora.** Claude lee `data/metrics.json` cada semana y ajusta temas, duración y ganchos.

## Carpetas
- `engine/` motor de animación (estilo flat) y `render_spec.py`.
- `queue/<fecha>-<tema>/` un vídeo: `spec.json` (animación) + `meta.json` (título, descripción, etiquetas, hora, estado).
  Para un vídeo largo ya montado: `"format": "long"` + `video.mp4` + `thumbnail.jpg`.
- `music/` pistas de la Biblioteca de audio de YouTube.
- `pipeline/` scripts de YouTube. `data/` estadísticas.

## Probar en local
```
pip install -r requirements.txt
python engine/render_spec.py queue/2026-11-14-4231-estructura-226/spec.json prueba.mp4
python engine/render_spec.py queue/2026-11-14-4231-estructura-226/spec.json hoja.jpg --sheet 2 8 14 20
python pipeline/validate.py
```

## Secretos (Settings → Secrets and variables → Actions)
`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` — se obtienen una vez con `python pipeline/get_token.py client_secret.json`.

Estados de `meta.json`: `draft` → `approved` → `scheduled` → `published` (o `failed`, con el motivo en `error`).
