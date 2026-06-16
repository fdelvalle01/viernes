"""Herramienta de diagnóstico para probar micrófono y mostrar RMS en tiempo real."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import numpy as np
    import sounddevice as sd
except ImportError as e:
    print(f"Error: Falta dependencia '{e.name}'. Instala con: pip install {e.name}")
    sys.exit(1)


def list_microphones() -> None:
    print("\nDispositivos de entrada disponibles:")
    try:
        devices = sd.query_devices(kind="input")
        if isinstance(devices, dict):
            print(f"  - {devices['name']} (channels: {devices['max_input_channels']})")
        else:
            for dev in devices:
                if dev["max_input_channels"] > 0:
                    print(f"  - {dev['name']} (channels: {dev['max_input_channels']})")
    except Exception as e:
        print(f"  No se pudieron listar dispositivos: {e}")


def test_microphone(sample_rate: int = 44100, block_size: int = 1024) -> None:
    print("=" * 50)
    print("DIAGNOSTICO: Microfono - RMS en tiempo real")
    print("=" * 50)

    list_microphones()

    print("\nPresiona Ctrl+C para salir.\n")
    print("-" * 50)

    rms_history = []

    def callback(indata, frames, time_info, status) -> None:
        if status:
            print(f"Warning: {status}")
        rms = float(np.sqrt(np.mean(np.square(indata))))
        rms_history.append(rms)
        if len(rms_history) > 100:
            rms_history.pop(0)
        avg_rms = sum(rms_history) / len(rms_history) if rms_history else 0
        bar = "#" * int(rms * 50)
        print(f"RMS: {rms:.4f} | Avg: {avg_rms:.4f} | {bar[:50]}")

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            blocksize=block_size,
            channels=1,
            dtype="float32",
            callback=callback,
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n" + "-" * 50)
        print("Interrumpido por usuario.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Asegurate de que el microfono este habilitado en Windows.")


if __name__ == "__main__":
    test_microphone()