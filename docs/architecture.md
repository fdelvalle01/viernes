# Architecture

`src.main` orquesta el loop principal y mantiene el acoplamiento bajo entre camara, vision, audio, acciones locales y UI.

## Flujo principal

1. `CameraService` abre la camara local y entrega frames BGR.
2. `HandTracker` convierte el frame a RGB y ejecuta MediaPipe Hands.
3. `GestureDetector` clasifica la mano como `open`, `closed`, `unknown` o `none`.
4. `AppState` aplica el umbral de gesto sostenido y conserva estado compartido.
5. Si el estado esta `ACTIVE`, `MouseController` mueve el mouse usando el landmark configurado.
6. `OverlayRenderer` dibuja landmarks, conexiones y estado sobre el frame.
7. `VoiceListener` y `ClapDetector` corren en hilos opcionales y actualizan `AppState` mediante callbacks.

## Modulos

- `camera/camera_service.py`: captura OpenCV y configuracion de camara.
- `vision/hand_tracker.py`: integracion con MediaPipe.
- `vision/gesture_detector.py`: heuristica de mano abierta/cerrada.
- `control/mouse_controller.py`: mapeo de coordenadas normalizadas a pantalla, suavizado y limite de saltos.
- `control/system_actions.py`: acciones locales permitidas.
- `audio/voice_listener.py`: comandos de voz offline con Vosk.
- `audio/clap_detector.py`: deteccion simple de aplausos por RMS.
- `ui/overlay_renderer.py`: ventana y textos sobre video.
- `core/app_state.py`: estado thread-safe y cooldowns.
- `core/config_loader.py`: carga de YAML con defaults.

## Principios de seguridad

- Sin servicios cloud.
- Sin envio de imagen o audio fuera del equipo.
- Sin comandos destructivos.
- Cierre por teclado con `q` o `esc`.
- Audio opcional: si falla microfono o modelo, el loop de camara continua.

## Futuras fases

- Clasificador de gestos entrenado.
- Clicks, scroll y drag con gestos especificos.
- HUD mas avanzado.
- Control seguro de ventanas con allowlist.
- Perfil por usuario para sensibilidad y calibracion.
