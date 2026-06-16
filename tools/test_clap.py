"""Herramienta de diagnóstico para probar detección de aplausos."""

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


def test_clap(
    sample_rate: int = 44100,
    block_size: int = 1024,
    threshold: float = 0.65,
    cooldown: float = 1.2,
) -> None:
    print("=" * 50)
    print("DIAGNOSTICO: Detector de aplausos")
    print("=" * 50)
    print(f"Threshold: {threshold}")
    print(f"Cooldown: {cooldown}s")
    print("\nPresiona Ctrl+C para salir.")
    print("-" * 50)

    last_clap = 0.0
    clap_count = 0

    def callback(indata, frames, time_info, status) -> None:
        nonlocal last_clap, clap_count
        if status:
            print(f"Warning: {status}")
        rms = float(np.sqrt(np.mean(np.square(indata))))
        now = time.monotonic()

        bar = "#" * int(rms * 50)
        level_str = f"{rms:.4f}"

        if rms >= threshold and now - last_clap >= cooldown:
            clap_count += 1
            last_clap = now
            print(f"[CLAP #{clap_count}] {level_str} | {bar[:50]} | {time.strftime('%H:%M:%S')}")
        else:
            print(f"RMS: {level_str} | {bar[:50]}")

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            blocksize=block_size,
            channels=1,
            dtype="float32",
            callback=callback,
        ):
            print("Escuchando... (aplaude para probar)")
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n" + "-" * 50)
        print(f"Total de aplausos detectados: {clap_count}")
    except Exception as e:
        print(f"\nError: {e}")
        print("Asegurate de que el microfono este habilitado en Windows.")


if __name__ == "__main__":
    test_clap()