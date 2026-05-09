#import "style.typ": conf

#show: doc => conf(
  title: [Project PreTensor: Optimization Pipeline Engineering Report],
  doc,
)

#include "00-frontmatter.typ"

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
