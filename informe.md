---
title: File Transfer
subtitle: |
  | Facultad de Ingeniería, Universidad de Buenos Aires
  | [75.43 · 75.33 · 95.60] Introducción a los Sistemas Distribuidos
  |
  | 29 de octubre de 2021
titlepage: true
colorlinks: true
linkcolor: purple
urlcolor: purple
papersize: a4
geometry: margin=2.5cm
header-includes: |
  \usepackage{fancyhdr}
  \pagestyle{fancy}
  \fancyhead[L]{2021C2}
  \fancyhead[R]{[71.59] Técnicas de Programación Concurrente I \\ TP1: File Transfer}

  \usepackage{listings}
  \lstset{
      breaklines=true,
      breakatwhitespace=true,
      basicstyle=\ttfamily\footnotesize,
      frame=l,
      framesep=12pt,
      xleftmargin=12pt,
  }
  \let\OldTexttt\texttt


  \author{
    \begin{tabular}{cr}
    Albanesi, Marco   & 86063 \\
    del Mazo, Federico  & 100029 \\
    Di Santo, Javier Mariano  & 101696 \\
    Dvorkin, Camila  & 101109 \\
    Rombolá, Juan Pablo & 97131 \\
    \end{tabular}
  }

include-before: \renewcommand{\texttt}[1]{\OldTexttt{\color{magenta}{#1}}}
---

<!-- para generar el informe: pandoc informe.md -o informe.pdf -->

# Introducción

# Hipótesis y suposiciones realizadas

# Implementación

La entrega debe contar con un informe donde se demuestre conocimiento de la interfaz de sockets, así como también los resultados de las ejecuciones de prueba (capturas de ejecución de cliente y logs del servidor). El informe debe describir la arquitectura de la aplicación. En particular, se pide detallar el protocolo de red implementado para cada una de las operaciones requeridas.

Comparar la performance de la versión GBN del protocolo y la versión Stop&Wait utilizando archivos de distintos tamaños y bajo distintas configuraciones de pérdida de paquetes.

# Preguntas a responder

> _Describa la arquitectura Cliente-Servidor._

La arquitectura...

> ¿Cuál es la función de un protocolo de capa de aplicación?

> Detalle el protocolo de aplicación desarrollado en este trabajo.

> La capa de transporte del stack TCP/IP ofrece dos protocolos: TCP y UDP. ¿Qué servicios proveen dichos protocolos? ¿Cuáles son sus características? ¿Cuando es apropiado utilizar cada uno?

# Dificultades encontradas

# Conclusión
