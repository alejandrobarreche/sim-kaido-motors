# Informe didáctico en LaTeX

Abrir **[report.pdf](report.pdf)** para leer el informe completo.

## Compilar

Desde esta carpeta, con pdfLaTeX:

```bash
pdflatex -interaction=nonstopmode -halt-on-error report.tex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
```

En una compilación limpia, la tercera pasada estabiliza las referencias después
de paginar el índice. Si se dispone de `latexmk`, este gestiona las pasadas:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error report.tex
```

No se necesita ejecutar Python, los notebooks, BibTeX ni programas externos para
compilar. Los paquetes utilizados son habituales de una distribución completa de
TeX Live/MacTeX; el documento está preparado para **pdfLaTeX**, sin fuentes del
sistema ni `shell-escape`.

## Contenido

- `report.tex`: formato, portada, índice e integración del informe.
- `secciones/`: explicación de las fases, resultados y anexos.
- `tablas/`: tablas numéricas de la ejecución revisada.
- `figuras/`: gráficos generados por los notebooks y logo del enunciado.
- `datos/`: pequeñas tablas de resultados utilizadas por las gráficas vectoriales
  dibujadas directamente en LaTeX.

La carpeta es autocontenida para compilar. Las tablas y las figuras constituyen una
instantánea de la ejecución de referencia del **10 de octubre de 2026**; no vuelven
a estimar el modelo durante la compilación. Si cambian los resultados del proyecto,
deben actualizarse las tablas, los datos de gráficos y las interpretaciones citadas.
Cada figura y tabla indica su fuente dentro de `../../results`.

El diseño toma del enunciado la tipografía serif, la estructura académica, la
numeración de apartados y los acentos azules. Añade recursos didácticos para explicar
el proceso. Los autores del caso se citan como fuente, no como autores del informe.
