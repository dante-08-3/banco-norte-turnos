# Banco Norte · Sistema de turnos

Aplicación de muestra para una sucursal bancaria: genera turnos, asigna al cliente a la primera mesa libre y mantiene a los demás en una fila FIFO. Al finalizar una atención, la mesa llama automáticamente al siguiente turno.

## Stack

- Frontend Angular 19 (español, adaptable a móvil)
- API FastAPI en Python
- Cuatro mesas de atención

## Ejecutar localmente

En una terminal, instala los paquetes del frontend con `npm install` y luego `npm start`. En otra terminal, crea un entorno virtual, instala `requirements.txt` y ejecuta `uvicorn api.index:app --reload`. Abre `http://localhost:4200` para tomar turnos y `/pantalla` en una segunda pantalla para mostrar el turno llamado.

## Despliegue

El frontend se compila a `dist/browser`; las rutas `/api/*` se envían a la función Python. La API mantiene la cola en memoria, adecuada para una demostración local en un único proceso. Las funciones de Vercel son efímeras y pueden ejecutarse en instancias distintas: para operación real con varios dispositivos hace falta conectar una base de datos compartida y proteger las acciones de operador con autenticación.

## Flujo

1. Tomar un turno asigna una mesa libre o añade el turno al final de la fila.
2. El tablero consulta estado periódicamente.
3. Finalizar atención libera la mesa y llama al turno más antiguo, si lo hay.
