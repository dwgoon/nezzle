
# Contents
1. [GUI Examples](#GUI-Examples)
    - [Convert node types](#Convert-node-types)
    - [Convert link types](#Convert-link-types)
    - [Undo & redo in history](#Undo-&-redo-in-history)
    - [Save & load networks](#Save-&-load-networks)    
    - [Export images](#Export-images)
    - [Copy to clipboard](#Copy-to-clipboard)

2. [Code Examples](#Code-Examples)
    - [Nodes](#Nodes)
    - [Links](#Links)
    - [Arrows](#Arrows)
    - [Labels](#Labels)
    - [Files](#Files)
    - [Applications](#Applications)


# GUI Examples

### Convert node types
<table>
<tr><td>
<img src="images/convert_node_types.gif" alt="Drawing" width="600px"/>
</td></tr>
</table>

### Convert link types
<table>
<tr><td>
<img src="images/convert_link_types.gif" alt="Drawing" width="600px"/>
</td></tr>
</table>

### Undo & redo in history
<img src="images/undo_redo_in_history.gif" alt="Drawing" width="800px"/>

### Save & load networks
<img src="images/save_load_networks.gif" alt="Drawing" width="800px"/>

### Export images
<img src="images/export_images.gif" alt="Drawing" width="800px"/>

### Copy to clipboard
<img src="images/copy_to_clipboard.gif" alt="Drawing" width="800px"/>



# Code Examples

- Each example shows how network visualization can be automated in different ways.
- These codes are basic templates for new tasks.
- The Python source code (i.e., module) should include `update(nav, net)` function, which is called by Nezzle.
  <p><img src="images/run_code_update.png" alt="Drawing" width="600px"/></p>
- Any Python module and package can be a plugin for extending the functionality of Nezzle.
  <p><img src="images/nezzle_plugin.png" alt="Drawing" width="600px"/></p>


### Nodes

<table>
  <tr>
    <th> Visualization </th>
    <th> Code </th>
  </tr>
  <tr>
  <td>
  <img src="images/node01.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF

  from nezzle.graphics import EllipseNode
  from nezzle.graphics import Network


  def update(nav, net):
      net = Network("A single node")  # Overwrite the "net" variable.

      node = EllipseNode("NODE", 40, 40, pos=QPointF(0, 0))
      node['FILL_COLOR'] = Qt.yellow
      node["BORDER_COLOR"] = Qt.black
      node['BORDER_WIDTH'] = 2
      net.add_node(node)

      nav.append_item(net)
  ```

  </td>
  </tr>

  <tr>
  <td>
  <img src="images/node02.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      net = Network("A single node with a label")
  
      node = EllipseNode("NODE", 40, 40, pos=QPointF(0, 0))
      node['FILL_COLOR'] = Qt.yellow
      node["BORDER_COLOR"] = Qt.black
      node['BORDER_WIDTH'] = 2
  
      label = TextLabel(node, "A")
      label["FONT_SIZE"] = 20
      label["TEXT_COLOR"] = Qt.black
      label.align()
  
      net.add_node(node)
      net.add_label(label)
  
      nav.append_item(net)
  ```

  </td>
  </tr>

  <tr>
  <td>
  <img src="images/node03.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      net = Network("Three nodes of different colors")
      node_colors = [Qt.red, Qt.green, Qt.blue]
      text_colors = [Qt.black, Qt.black, Qt.white]
      for i, name in enumerate(["A", "B", "C"]):          
          # Node ID (i.e., iden) should be different.
          node = EllipseNode(iden=name,
                             width=40,
                             height=40,
                             pos=QPointF(-80 + 80*i, -80 + 80*i))
          node['FILL_COLOR'] = node_colors[i]
          node["BORDER_COLOR"] = Qt.black
          node['BORDER_WIDTH'] = 2
  
          label = TextLabel(node, name)
          label["FONT_SIZE"] = 20
          label["TEXT_COLOR"] = text_colors[i]
          label.align()
  
          net.add_node(node)
          net.add_label(label)
      # end of for
      nav.append_item(net)
  ```

  </td>
  </tr>

  <tr>
  <td>
  <img src="images/node04.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  from qtpy.QtGui import QColor
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      net = Network("Five nodes of different sizes")
      num_nodes = 5
      for i in range(num_nodes):
          name = str(i)
          node = EllipseNode(name,
                             20 + 10*i,
                             40,
                             pos=QPointF(-200 + 80*i, -100 + 20*i))
          node['FILL_COLOR'] = QColor(153, 0, 153)
          node["BORDER_COLOR"] = Qt.black
          node['BORDER_WIDTH'] = 2
  
          label = TextLabel(node, name)
          label["FONT_SIZE"] = 16 + 2*i
          label["TEXT_COLOR"] = Qt.white
          label.align()
  
          net.add_node(node)
          net.add_label(label)
      # end of for      
      nav.append_item(net)
  ```
  </td>
  </tr>

  <tr>
  <td>
  <img src="images/node05.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  from qtpy.QtGui import QColor
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      net = Network("Five rectangle nodes of different sizes")
      num_nodes = 5
      for i in range(num_nodes):
          name = str(i)
          node = EllipseNode(name,
                             20 + 10 * i,
                             40,
                             pos=QPointF(-200 + 80 * i, 100 - 20 * i))
          node['FILL_COLOR'] = QColor(153, 51, 0)
          node["BORDER_COLOR"] = Qt.black
          node['BORDER_WIDTH'] = 2
  
          label = TextLabel(node, name)
          label["FONT_SIZE"] = 16 + 2 * i
          label["TEXT_COLOR"] = Qt.white
          label.align()
  
          net.add_node(node)
          net.add_label(label)
      # end of for    
      nav.append_item(net)
  ```
  </td>
  </tr>


  <tr>
  <td>
  <img src="images/node06.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  import numpy as np
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  from qtpy.QtGui import QColor
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      color_white = np.array([255, 255, 255, 0])
      color_up = np.array([255, 0, 0, 0])
      color_dn = np.array([0, 0, 255, 0])
  
      num_nodes = 30
  
      x = np.random.uniform(-200, 200, num_nodes)  # X coordinates
      y = np.random.uniform(-200, 200, num_nodes)  # Y coordinates
      z = np.random.uniform(-1, 1, num_nodes)  # Some values to display in color
      abs_z = np.abs(z)
      norm_abs_z = abs_z / abs_z.max()
  
      net = Network("Node color mapping")
      for i in range(num_nodes):
          name = str(i)
          node = EllipseNode(name, 40, 40, pos=QPointF(x[i], y[i]))
  
          if z[i] > 0:
              color = color_white + norm_abs_z[i] * (color_up - color_white)
          elif z[i] <= 0:
              color = color_white + norm_abs_z[i] * (color_dn - color_white)
  
          color[3] = 255
          node['FILL_COLOR'] = QColor(*color)
          node["BORDER_COLOR"] = Qt.black
          node['BORDER_WIDTH'] = 2
  
          label_name = TextLabel(node, name)
          label_name["FONT_SIZE"] = 16
          label_name["TEXT_COLOR"] = Qt.white
          label_name.align()
  
          lightness = QColor(node['FILL_COLOR']).lightness()
          if lightness < 200:
              label_name['TEXT_COLOR'] = Qt.white
              label_name['FONT_BOLD'] = True
          else:
              label_name['TEXT_COLOR'] = Qt.black
              label_name['FONT_BOLD'] = False
  
          net.add_node(node)
          net.add_label(label_name)
      # end of for
      nav.append_item(net)
  ```
  </td>
  </tr>
</table>

## Links
<table>
  <tr>
    <th> Visualization </th>
    <th> Code </th>
  </tr>
  <tr>
  <td>
  <img src="images/link01.png" alt="Drawing" width="300px"/>
  </td>
  <td>

  ```python
  from qtpy.QtCore import Qt
  from qtpy.QtCore import QPointF
  
  from nezzle.graphics import EllipseNode
  from nezzle.graphics import TextLabel
  from nezzle.graphics import StraightLink
  from nezzle.graphics import Network
  
  
  def update(nav, net):
      net = Network("A single edge")
  
      src = EllipseNode("SRC", 40, 40, pos=QPointF(-60, 0))
      src['FILL_COLOR'] = Qt.yellow
      src["BORDER_COLOR"] = Qt.black
      src['BORDER_WIDTH'] = 2
  
      tgt = EllipseNode("TGT", 40, 40, pos=QPointF(60, 0))
      tgt['FILL_COLOR'] = Qt.yellow
      tgt["BORDER_COLOR"] = Qt.black
      tgt['BORDER_WIDTH'] = 2
  
      link = StraightLink("LINK", src, tgt, width=4)
  
      label_src = TextLabel(src, "A")
      label_src["FONT_SIZE"] = 20
      label_src["TEXT_COLOR"] = Qt.black
      label_src.align()
  
      label_tgt = TextLabel(tgt, "B")
      label_tgt["FONT_SIZE"] = 20
      label_tgt["TEXT_COLOR"] = Qt.black
      label_tgt.align()
  
      net.add_node(src)
      net.add_node(tgt)
      net.add_link(link)
      net.add_label(label_src)
      net.add_label(label_tgt)
  
      nav.append_item(net)
  ```

  </td>
  </tr>
</table>


## Arrows


## Labels


## Files

## Applications
