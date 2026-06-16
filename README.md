# RV Camera Controller

MVP local para Windows que usa la camara del computador para detectar una mano con MediaPipe, dibujar landmarks en una ventana de OpenCV y mover el mouse cuando el sistema esta activo.

Todo el procesamiento ocurre localmente. La app no envia imagen, audio ni comandos a servicios externos.

## MVP 0.1 - Estado

Esta version es el primer release funcional. Los siguientes comandos estan implementados y verificados:

| Gesto / Voz | Accion |
|-------------|--------|
| mano abierta sostenida | activar control de mouse |
| mano cerrada sostenida | desactivar control de mouse |
| `activar` | activar control de mouse |
| `desactivar` | desactivar control de mouse |
| `abrir navegador` / `navegador` | abrir Google en navegador |
| `salir` | cerrar aplicacion |
| aplauso | alternar active/inactive |
| `q` / `esc` | cerrar aplicacion |

## Funciones incluidas

- Camara local con OpenCV.
- Landmarks y conexiones de mano dibujados en tiempo real.
- Estado visible `ACTIVE` / `INACTIVE`.
- Mano abierta sostenida: activa control.
- Mano cerrada sostenida: desactiva control.
- Movimiento de mouse por landmark del dedo indice con suavizado y limite de saltos.
- Comandos de voz offline con Vosk, si existe un modelo local.
- Deteccion simple de aplausos por umbral de volumen con cooldown.
- Comando `abrir navegador` usando el navegador predeterminado de Windows.
- Cierre seguro con `q` o `esc`.
- `pyautogui.FAILSAFE` activo.

## Instalacion en Windows

Requisitos:

- Python 3.11 o superior.
- Camara disponible.
- Opcional para voz/aplausos: microfono disponible.

Desde `d:\IA\rv-camera-controller`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si `sounddevice` falla durante instalacion o ejecucion, revisa que Windows tenga un dispositivo de entrada activo. La app puede seguir funcionando con camara y gestos aunque voz o aplausos queden deshabilitados.

## Ejecucion

```powershell
python -m src.main
```

Si Windows responde que no encontro `python`, prueba:

```powershell
py -m src.main
```

## Modelo offline de Vosk

La voz es opcional. Para activarla, descarga un modelo local de Vosk en espanol y colocalo en:

```text
models/vosk-es
```

La ruta puede cambiarse en `config/settings.yaml`:

```yaml
voice:
  enabled: true
  model_path: models/vosk-es
```

Si la carpeta no existe, la aplicacion muestra voz como deshabilitada y continua con camara, gestos y mouse.

## Configuracion

Archivo principal: `config/settings.yaml`.

Campos utiles:

- `camera.index`: cambia la camara si tienes mas de una.
- `camera.mirror`: espejo horizontal para control mas natural.
- `vision.gesture_hold_seconds`: tiempo que una mano abierta/cerrada debe sostenerse antes de cambiar estado.
- `vision.pointer_landmark`: landmark usado para mover el mouse. `8` es la punta del dedo indice.
- `mouse.smoothing`: suavizado del mouse. Mas bajo = mas suave/lento.
- `mouse.max_step_pixels`: limite de salto por actualizacion.
- `mouse.movement_margin`: margen para mapear el area visible al escritorio completo.
- `clap.threshold`: sensibilidad de aplauso. Baja el valor si no detecta; subelo si hay falsos positivos.
- `clap.cooldown_seconds`: tiempo minimo entre aplausos aceptados.

## Problemas comunes

### No abre la camara

- Prueba otro `camera.index`, por ejemplo `1` o `2`.
- Cierra Zoom, Teams u otra app que este usando la camara.
- Cambia `camera.use_dshow` a `false` si tu camara no funciona bien con DirectShow.

### El mouse tiembla demasiado

- Baja `mouse.smoothing`, por ejemplo `0.15`.
- Baja `mouse.max_step_pixels`.
- Aumenta `vision.min_tracking_confidence`.

### La voz no funciona

- Confirma que `models/vosk-es` existe y contiene un modelo Vosk valido.
- Confirma que el microfono esta habilitado en Windows.
- Puedes dejar `voice.enabled: false` para trabajar solo con gestos.

### El aplauso activa muchas veces

- Sube `clap.cooldown_seconds`.
- Sube `clap.threshold`.

## Diagnostico

Si la app no behave como esperas, usa estas herramientas de diagnostico:

```powershell
# Probar camara
python -m tools.test_camera

# Probar microfono (muestra RMS en vivo)
python -m tools.test_microphone

# Probar deteccion de aplausos
python -m tools.test_clap

# Validar modelo Vosk
python -m tools.test_voice_model
```

### Estado en el overlay

El panel superior muestra el estado de voz y aplausos:

- `Voice: disabled` = voice.enabled=false en config
- `Voice: starting` = iniciando...
- `Voice: listening` = microfono activo, esperando comandos
- `Voice: error` + mensaje = problema especifico mostrado
- `Clap: disabled` = clap.enabled=false en config
- `Clap: starting` = iniciando...
- `Clap: listening` = detector activo
- `Clap: 0.45` = nivel RMS actual
- `Clap: error` + mensaje = problema especifico mostrado

Si voz o aplausos fallan, la camara, gestos y mouse siguen funcionando normalmente.

## Seguridad del MVP 0.1

Esta version no cierra ventanas, no ejecuta comandos peligrosos y no usa APIs externas. La unica accion del sistema incluida es abrir el navegador predeterminado con `https://www.google.com`.

PyAutoGUI mantiene el failsafe activo: mover el cursor a una esquina de la pantalla puede interrumpir acciones de PyAutoGUI.
