import io

from pydub import AudioSegment


def chunk_audio(file_bytes: bytes) -> list[dict]:
    audio = AudioSegment.from_file(io.BytesIO(file_bytes))

    window_ms = 3000
    step_ms = 1500

    if len(audio) <= window_ms:
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")

        return [
            {
                "start_ms": 0,
                "end_ms": len(audio),
                "audio_bytes": buffer.getvalue(),
            }
        ]

    chunks = []

    for start_ms in range(0, len(audio) - window_ms + 1, step_ms):
        end_ms = start_ms + window_ms
        chunk = audio[start_ms:end_ms]

        buffer = io.BytesIO()
        chunk.export(buffer, format="wav")

        chunks.append(
            {
                "start_ms": start_ms,
                "end_ms": end_ms,
                "audio_bytes": buffer.getvalue(),
            }
        )

    return chunks