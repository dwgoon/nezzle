graph [
  node [
    id 0
    label "0"
    graphics [
      x -100.0
      y 0.0
      w 50.0
      h 50.0
      type "ellipse"
      fill "#ffff00"
      outline "#666666"
      width 4
    ]
  ]
  node [
    id 1
    label "1"
    graphics [
      x 100.0
      y 0.0
      w 50.0
      h 50.0
      type "rectangle"
      fill "#ff9933"
      outline "#000000"
      width 4
    ]
  ]
  edge [
    source 0
    target 1
    weight 0.5
    label "edge"
    graphics [
      width 8.0
      fill "&#34;#0000ff&#34;"
      type "quadCurve"
      line ""
      sourceArrow 0
      targetArrow "delta"
    ]
  ]
]
