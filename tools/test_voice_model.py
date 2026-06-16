"""Herramienta de diagnóstico para validar el modelo Vosk."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import get_config, get_project_root


def test_voice_model() -> None:
    print("=" * 50)
    print("DIAGNOSTICO: Modelo Vosk")
    print("=" * 50)

    config = get_config()
    voice_config = config.get("voice", {})
    enabled = voice_config.get("enabled", True)

    print(f"\nVoice enabled en config: {enabled}")

    if not enabled:
        print("\nVoice esta deshabilitado en settings.yaml")
        print("Para habilitar, cambia voice.enabled a true")
        return

    print("\n1. Verificando dependencia 'vosk'...", end=" ", flush=True)
    try:
        import vosk  # noqa: F401
        print("OK")
    except ImportError as e:
        print(f"ERROR")
        print(f"  vosk no esta instalado: {e}")
        print(f"  Instala con: pip install vosk")
        return

    print("2. Verificando dependencia 'sounddevice'...", end=" ", flush=True)
    try:
        import sounddevice as sd  # noqa: F401
        print("OK")
    except ImportError as e:
        print(f"ERROR")
        print(f"  sounddevice no esta instalado: {e}")
        print(f"  Instala con: pip install sounddevice")
        return

    model_path_raw = voice_config.get("model_path", "models/vosk-es")
    model_path = Path(model_path_raw)

    if not model_path.is_absolute():
        model_path = get_project_root() / model_path_raw

    print(f"\n3. Verificando ruta del modelo: {model_path}", end=" ", flush=True)
    if not model_path.exists():
        print("ERROR")
        print(f"  La carpeta del modelo no existe: {model_path}")
        print(f"  Descarga un modelo Vosk en espanol y coloca en: {model_path}")
        print(f"  Modelos: https://alphacephei.com/vosk/models")
        return
    print("OK")

    print("\n4. Cargando modelo Vosk...", end=" ", flush=True)
    try:
        from vosk import Model

        model = Model(str(model_path))
        print("OK")
    except Exception as e:
        print(f"ERROR")
        print(f"  No se pudo cargar el modelo: {e}")
        print(f"  El modelo puede estar corrupto o ser incompatible.")
        return

    sample_rate = voice_config.get("sample_rate", 16000)
    print(f"\n5. Probando reconocimiento (sample_rate={sample_rate})...", end=" ", flush=True)
    try:
        from vosk import KaldiRecognizer

        recognizer = KaldiRecognizer(model, sample_rate)
        test_audio = b"\x00" * (sample_rate // 10)
        result = recognizer.AcceptWaveform(test_audio)
        print("OK")
    except Exception as e:
        print(f"ERROR")
        print(f"  Fallo en reconocimiento: {e}")
        return

    print("\n" + "=" * 50)
    print("RESULTADO: Todo OK - El modelo Vosk esta listo")
    print("=" * 50)
    print("\nPuedes ejecutar python -m src.main y usar comandos de voz.")


if __name__ == "__main__":
    test_voice_model()