<div align="center">

# ❌ Triki ⭕

### El clásico tres en línea, en Python

**Juega contra una máquina que piensa o reta a un amigo en el mismo equipo.**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![tkinter](https://img.shields.io/badge/GUI-tkinter-ff6b57?style=for-the-badge)
![Sin dependencias](https://img.shields.io/badge/Dependencias-0-35e0c4?style=for-the-badge)
![Dificultades](https://img.shields.io/badge/Dificultades-3-ffcf5c?style=for-the-badge)

[**Jugar**](#-jugar-en-3-pasos) &nbsp;•&nbsp;
[**Qué incluye**](#-qué-incluye) &nbsp;•&nbsp;
[**Dificultades**](#-dificultades) &nbsp;•&nbsp;
[**Cómo piensa**](#-cómo-piensa-la-máquina)

</div>

---

## 🎮 Jugar en 3 pasos

**1. Ten Python instalado.** Necesitas Python 3.8 o superior. tkinter ya viene incluido en Windows y macOS. En Linux:

```bash
sudo apt install python3-tk
```

**2. Descarga el proyecto.** En esta página pulsa el botón verde **Code** y luego **Download ZIP**. Descomprime la carpeta.

**3. Ejecútalo.** Desde la carpeta del proyecto:

```bash
python triki.py
```

> En algunos sistemas el comando es `python3 triki.py`. No hay nada más que instalar.

---

## ✨ Qué incluye

| | |
|:--|:--|
| 🤖 **Contra la máquina** | Tres niveles, de despistada a imbatible. |
| 👥 **Dos jugadores** | Los dos en el mismo equipo, por turnos. |
| 🏆 **Marcador** | Victorias de cada jugador y empates, acumulados entre rondas. |
| 🔄 **Turnos justos** | Empieza uno distinto en cada ronda. |
| 🎨 **Interfaz propia** | Dibujada por completo en un `Canvas`, con fichas luminosas. |
| 🎉 **Animaciones** | Las fichas se trazan solas, la victoria se marca con una línea dorada y cae confeti. |
| 👆 **Vista previa** | Al pasar el mouse sobre una casilla libre aparece la ficha que pondrías. |
| 📦 **Un solo archivo** | Sin librerías externas. Solo Python y tkinter. |

---

## 🎚️ Dificultades

| Nivel | Reto | Cómo juega |
|:--|:--:|:--|
| 🟢 **Fácil** | ▰▱▱ | Juega casi siempre al azar. Solo una de cada cinco veces aprovecha un triunfo inmediato. |
| 🟡 **Media** | ▰▰▱ | Gana si puede, bloquea tus jugadas y prefiere el centro y las esquinas, pero una de cada cuatro veces se despista. |
| 🔴 **Difícil** | ▰▰▰ | Analiza todas las partidas posibles. **No se le puede ganar**: lo máximo que consigues es un empate. |

---

## 🕹️ Controles

| Acción | Cómo |
|:--|:--|
| Poner una ficha | Clic en una casilla vacía |
| Empezar otra ronda al terminar | Clic sobre el tablero |
| Reiniciar el tablero | Botón **Nueva ronda** |
| Volver al menú | Botón **← Menú** o tecla `Esc` |

Tú juegas con **X** y la máquina con **O**. Gana quien complete tres fichas en una fila, una columna o una diagonal.

---

## 🧠 Cómo piensa la máquina

<details>
<summary><b>Ver cómo funciona el nivel difícil</b></summary>

<br>

El nivel difícil usa el algoritmo **minimax**. Antes de mover, la máquina simula todas las partidas que podrían salir de cada jugada posible y le da un puntaje a cada final:

- **Gana la máquina:** puntaje positivo.
- **Pierde:** puntaje negativo.
- **Empate:** cero.

Después sube esos puntajes por el árbol de jugadas con una regla: en sus turnos elige el puntaje más alto, y en los tuyos supone que tú eliges el más bajo, es decir, que juegas lo mejor posible. Al final se queda con la casilla de mejor puntaje.

El puntaje también depende de la profundidad, así que prefiere ganar cuanto antes y perder lo más tarde posible. Si varias jugadas valen lo mismo, elige una al azar, y en el primer movimiento toma el centro o una esquina para que las partidas no sean siempre iguales.

Como el tablero es pequeño, puede revisar todas las posibilidades en un instante, y por eso nunca pierde.

</details>

---

## 📁 Estructura

```
triki/
├── triki.py          El juego completo
├── README.md         Esta página
├── LICENSE           Licencia MIT
└── .gitignore        Archivos que Git ignora
```

---

## 🛠️ Solución de problemas

<details>
<summary><b><code>ModuleNotFoundError: No module named 'tkinter'</code></b></summary>

<br>

Tu instalación de Python no incluye tkinter. En Debian o Ubuntu instálalo con `sudo apt install python3-tk`. En Fedora, con `sudo dnf install python3-tkinter`. En Windows y macOS, reinstala Python desde python.org y deja marcada la opción de tcl/tk.

</details>

<details>
<summary><b>La ventana se ve cortada en una pantalla pequeña</b></summary>

<br>

La ventana mide 520 × 760 píxeles y no se puede redimensionar. En pantallas de baja resolución puedes reducir los valores `ALTO`, `TAM` y `BY` al inicio de la clase `Triki`, dentro de `triki.py`.

</details>

<details>
<summary><b>El texto se ve con otra tipografía</b></summary>

<br>

El juego usa la primera fuente que encuentre entre Segoe UI, Poppins, Montserrat, Ubuntu, Helvetica Neue, Cantarell y DejaVu Sans. Si no hay ninguna, usa Helvetica. Para elegir una en concreto, edita la lista `preferidas` en `triki.py`.

</details>

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

<sub>Hecho con Python y tkinter</sub>

</div>
