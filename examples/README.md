# Code Examples

## Nodes

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
      """Update the navigation and network graphics,
         This function is called by Nezzle, when pushing the "run" button.

      Args:
          nav: the navigation that adds network items.
          net: the currently selected network item.
      """

      net = Network("A single node")

      node = EllipseNode('SRC1', 40, 40, pos=QPointF(0, 0))
      node['FILL_COLOR'] = Qt.yellow
      node["BORDER_COLOR"] = Qt.black
      node['BORDER_WIDTH'] = 2
      net.add_node(node)

      nav.append_item(net)
  ```

  </td>
  </tr>
</table>

## Links


## Arrows


## Labels
