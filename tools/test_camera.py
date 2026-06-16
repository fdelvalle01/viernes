"""Herramienta de diagnóstico para probar cámaras disponibles."""

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def list_cameras(max_index: int = 4) -> None:
    print("=" * 50)
    print("DIAGNOSTICO: Camaras disponibles")
    print("=" * 50)

    available = []

    for i in range(max_index):
        print(f"\nProbando camara index={i}...", end=" ", flush=True)
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"OK - {width}x{height} @ {fps:.1f} FPS")
            available.append(i)
            cap.release()
        else:
            print("no disponible")

    print("\n" + "=" * 50)
    if available:
        print(f"Camaras disponibles: {available}")
    else:
        print("No se detectaron camaras disponibles")
    print("=" * 50)


if __name__ == "__main__":
    list_cameras()