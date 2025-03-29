# Semáforos "vivos"

## Descripción General

Este proyecto es un simulador de semáforos interactivo y detallado desarrollado en Python utilizando PyQt6, que modela un cruce de cuatro direcciones con múltiples características avanzadas:

- Semáforos vehiculares y peatonales inteligentes
- Gestión dinámica del tráfico
- Visualización en tiempo real
- Análisis de flujo de tráfico
- Modelo de Red de Petri para estados de semáforos

## Características Principales

### 1. Gestión de Semáforos
- Semáforos para cuatro direcciones: Norte, Sur, Este, Oeste
- Estados: Verde, Amarillo, Rojo
- Semáforos peatonales con estados Rojo y Blanco
- Sistema de tokens para rastrear cambios de estado

### 2. Control de Tráfico Inteligente
- Detección automática de densidad de tráfico
- Priorización dinámica de direcciones con alto volumen de tráfico
- Extensión de tiempo en verde para direcciones congestionadas

### 3. Simulación de Vehículos
- Generación de vehículos en diferentes carriles
- Visualización de vehículos con colores según su destino
- Movimiento realista considerando el estado de los semáforos
- Detección de intersecciones y puntos de no retorno

### 4. Interfaz de Usuario Interactiva
- Control de velocidad de simulación
- Botones para iniciar, pausar, y reiniciar
- Generación manual y automática de tráfico
- Pestañas para Simulación y Red de Petri

### 5. Visualización Avanzada
- Diagrama de Red de Petri para estados de semáforos
- Contadores de tráfico en cada dirección
- Leyenda de colores para vehículos
- Vista detallada de la intersección

## Requisitos del Sistema

- Python 3.8+
- PyQt6
- Librerías estándar de Python

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/simulador-semaforos.git
cd simulador-semaforos
```

2. Instalar dependencias
```bash
pip install PyQt6
```

## Ejecución

```bash
python simulador_semaforos.py
```

## Controles de Simulación

![image](https://github.com/user-attachments/assets/25a63eed-81fd-45a7-aefb-ceeda7e1c8b1)


### Botones de Control
- **Iniciar**: Comienza la simulación
- **Pausar**: Detiene la simulación
- **Paso a Paso**: Avanza un paso en la simulación
- **Reiniciar**: Restablece todos los parámetros

### Control de Velocidad
- Deslizador para ajustar la velocidad de simulación
- Rango: 1x - 10x

### Control de Tráfico
- Botones para agregar vehículos manualmente en cada dirección
- Spinner para control de densidad de tráfico automático

## Pestañas

### Simulación
- Vista principal del cruce
- Semáforos vehiculares y peatonales
- Contadores de tráfico
- Vehículos en movimiento

### Red de Petri
- Diagrama de estados y transiciones
- Visualización del estado actual
- Marcación de estados priorizados

## Funcionalidades Avanzadas

- **Priorización Dinámica**: Ajusta los semáforos según la densidad de tráfico
- **Análisis de Tráfico**: Monitoreo continuo de flujo vehicular
- **Modelo de Intersección Realista**: Considera giros, velocidades y puntos de no retorno

## Personalización

Puedes modificar fácilmente:
- Tiempos de semáforos
- Patrones de tráfico
- Comportamiento de vehículos

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue o envíe un pull request.

## Licencia

[Especificar la licencia, por ejemplo MIT]

## Autor

[Su nombre o información de contacto]

## Notas Técnicas

- Implementado con programación orientada a objetos
- Uso extensivo de máquinas de estado
- Simulación basada en eventos discretos
