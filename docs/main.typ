#import "../mydocs/style.typ": conf

#show: doc => conf(
  title: [Project PreTensor: Optimization Pipeline Engineering Report],
  doc,
)

#grid(
  columns: (1fr, 1fr),
  align(left)[#image("../typst/assets/logo1.jpg", height: 1.5cm)],
  align(right)[#image("../typst/assets/logo2.jpg", height: 1.5cm)]
)

#align(center)[
  #v(0.5em)
  #text(size: 20pt, weight: "bold")[Project PreTensor]
  
  #v(0.2em)
  #text(size: 13pt)[Optimization Pipeline Engineering Report]
  
  #v(0.5em)
  #text(size: 10pt)[An analysis of pre-tensor token contraction for LLM inference]
  
  #v(1.5em)
  
  #align(center)[
    #block(
      fill: rgb("#fafafa"),
      inset: 1em,
      radius: 0.1em,
      stroke: (left: 3pt + rgb("#e03b24"), rest: 0.5pt + rgb("#e0e0e0")),
      align(left)[
        #text(size: 11pt, weight: "bold", fill: rgb("#e03b24"))[PRESENTED BY] \
        #v(0.2em)
        #text(size: 13pt, weight: "bold")[Mohamed Ahmed Mohamed Ali Shehata] \
        #text(size: 10pt, fill: rgb("#555555"))[*Student ID:* 202203567]
        
        #v(0.8em)
        #text(size: 11pt, weight: "bold", fill: rgb("#e03b24"))[EVALUATED BY] \
        #v(0.2em)
        #text(size: 10pt)[
          Dr. Reham Hussein \
          Eng. Shady Badir \
          Eng. Noha Rashad
        ]
      ]
    )
  ]
  
  #v(0.5em)
]

#outline(title: "Table of Contents", depth: 2)

#v(2em)

#include "01-introduction.typ"
#include "02-dataset.typ"
#include "03-methodology.typ"
#include "04-system-design.typ"
#include "05-results.typ"
#include "07-evaluation.typ"
#include "06-conclusion.typ"

= References
#bibliography("refs.bib", title: none, style: "ieee")
