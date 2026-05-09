#set heading(numbering: none)

#grid(
  columns: (1fr, 1fr),
  align: (left, right),
  image("assets/logo1.jpg", width: 40%),
  image("assets/logo2.jpg", width: 40%)
)

#v(3em)

#block(
  width: 100%,
  fill: black,
  inset: (x: 2em, y: 3em),
)[
  #text(fill: white, size: 28pt, weight: "bold")[
    PROJECT PRETENSOR \
    OPTIMIZATION PIPELINE
  ]
  #v(0.5em)
  #line(length: 15%, stroke: 4pt + rgb("#e03b24"))
  #v(1em)
  #text(fill: rgb("#cccccc"), size: 14pt)[
    An analysis of pre-tensor token contraction for LLM inference
  ]
]

#v(1.5em)

#block(
  width: 100%,
  fill: rgb("#f5f5f5"),
  inset: 1.5em,
)[
  #grid(
    columns: (1fr, 1fr),
    row-gutter: 1.5em,
    [
      #text(fill: rgb("#e03b24"), weight: "bold", size: 9pt)[COURSE] \
      Natural Language Processing \
      #v(0.5em)
      #text(fill: rgb("#e03b24"), weight: "bold", size: 9pt)[EVALUATED BY] \
      Dr. Reham Hussein \
      Eng. Shady Badir \
      Eng. Noha Rashad
    ],
    [
      #text(fill: rgb("#e03b24"), weight: "bold", size: 9pt)[INSTITUTION] \
      Faculty of Computer Science & Info. Systems \
      #v(0.5em)
      #text(fill: rgb("#e03b24"), weight: "bold", size: 9pt)[DATE] \
      May 2026
    ]
  )
]

#v(3em)

#align(center)[
  #text(fill: rgb("#e03b24"), weight: "bold", size: 11pt)[PRESENTED BY] \
  #v(0.2em)
  #text(size: 14pt, weight: "bold")[Mohamed Ahmed Mohamed Ali Shehata] \
  #text(size: 10pt, fill: rgb("#555555"))[*Student ID:* 202203567] \
  #v(0.8em)
  #link("https://github.com/Shehata-git/PreTensor")[
    #box(height: 1.1em, baseline: 25%, image.decode("<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='#e03b24' viewBox='0 0 16 16'><path d='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8'/></svg>", format: "svg"))
    #h(0.3em)
    #text(size: 10pt, weight: "bold", fill: rgb("#e03b24"))[Repository Link]
  ]
]

#pagebreak()

= Abstract

This report details the engineering and implementation of Project PreTensor, a VRAM-efficient RAG memory engine designed to address attention dilution and context bloat in Large Language Models (LLMs). By utilizing a pre-tensor token contraction pipeline—including SQLite session management, CPU-bound ONNX embeddings (nomic-embed-text), and local semantic retrieval via Qdrant—the system enables long-term memory without the overhead of full-context prompts. We evaluate the system using a dual-methodology A/B test (Method A: Standard vs. Method B: Semantic) across various multi-turn conversation scenarios, monitoring live metrics such as latency, token efficiency, and VRAM utilization through a modern, responsive GUI.

#line(length: 100%)
