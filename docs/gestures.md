# Gestures

## Mano abierta

Activa el sistema cuando se mantiene durante `vision.gesture_hold_seconds`.

Heuristica actual:

- MediaPipe entrega 21 landmarks.
- Se cuentan dedos extendidos comparando distancia de punta y articulacion con la muneca.
- Si hay 4 o mas dedos extendidos, el gesto se considera `open`.

## Mano cerrada

Desactiva el sistema cuando se mantiene durante `vision.gesture_hold_seconds`.

Heuristica actual:

- Si hay 1 o menos dedos extendidos, el gesto se considera `closed`.

## Desconocido o sin mano

- `unknown`: hay mano, pero no se puede clasificar de forma clara.
- `none`: MediaPipe no detecto mano.

Estos estados no cambian `ACTIVE` / `INACTIVE`.

## Movimiento del mouse

Cuando el sistema esta `ACTIVE`, se usa `vision.pointer_landmark` para mover el cursor. Por defecto:

- `8`: punta del dedo indice.

El controlador aplica:

- margen de mapeo para aprovechar toda la pantalla,
- suavizado exponencial,
- limite maximo de pixeles por actualizacion.

## Consejos de uso

- Usa una mano visible completa dentro del encuadre.
- Evita fondos con mucho movimiento.
- Si el cambio de estado ocurre muy rapido, sube `vision.gesture_hold_seconds`.
- Si cuesta activar/desactivar, baja levemente `vision.min_detection_confidence`.
