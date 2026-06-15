import os
import shutil
import tempfile
from pathlib import Path

import yt_dlp

from transcriptorpy.fuente_contenido import ErrorObtencionContenido


class FuenteYoutubeYtdlp:
    def obtener(self, url: str, ruta_destino: str) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            opciones = {
                "format": "bestaudio/best",
                "outtmpl": str(Path(tmp_dir) / "audio.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                # yt-dlp usa urllib (no httpx), por lo que no podemos inyectarle
                # un SSLContext personalizado. Cuando SSL_CERT_FILE está presente
                # hay un proxy SSL local (p.ej. Avast Web Shield) cuya CA no está
                # en el bundle de Python; desactivamos la verificación solo en ese
                # entorno de desarrollo.
                "nocheckcertificate": bool(os.environ.get("SSL_CERT_FILE")),
            }
            try:
                with yt_dlp.YoutubeDL(opciones) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError as exc:
                raise ErrorObtencionContenido(str(exc)) from exc
            archivos = sorted(
                f for f in Path(tmp_dir).iterdir()
                if f.is_file() and not f.name.endswith(".part")
            )
            if not archivos:
                raise ErrorObtencionContenido("yt-dlp no generó ningún archivo de audio")
            shutil.move(str(archivos[0]), ruta_destino)
