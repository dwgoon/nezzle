<img src="nezzle/resources/logo.png" alt="Drawing" width="395px"/>


## Introduction 
- Nezzle is a programmable and interactive visualization software for small-scale networks (N < 100).
- Nezzle was initially developed to visualize biological networks such as 
  [signaling networks](https://www.nature.com/articles/s41598-018-23643-5).
- Nezzle repesents **Ne**t + Pu**zzle**, because adjusting nodes and edges of a network for visualization is similar to playing a puzzle.
- Nezzle is currently under active development.
-  Consider ["Cytoscape"](https://cytoscape.org/) or ["Gephi"](https://gephi.org/) for large-scale networks.
 
## Features
- Lightweight, programmable, detailed visualization of small-scale networks for high quality figures.
- Highly customizable visualization of networks with user-defined source codes.
- Manual curation of the positions of nodes and edges by adjusting the graphics in GUI.
- Interactive programming to modify both data and graphics of networks in the GUI console.
- The GUI depends on Python bindings for [`Qt`](https://www.qt.io/)
  such as [`PyQt`](https://riverbankcomputing.com/software/pyqt)
  (abstracted by [`QtPy`](https://github.com/spyder-ide/qtpy) in this project).


## Installation
First, clone the recent version of this repository.

```
git clone https://github.com/dwgoon/nezzle.git nezzle
```

Now, we need to install Nezzle as a module.

```
cd nezzle
python setup.py install
```

## Execution

```
python nezzle.py
```

## Examples

### Mapping dynamics data to graphics 
<p>
  <img src="examples/images/2nnfl-time-series.png" alt="Drawing" width="400px"/>
</p>
<p>
  <img src="examples/images/2nnfl-network.gif" alt="Drawing" width="400px"/>
</p>

### Adjusting network graphics through GUI
<img src="assets/demo01.gif" alt="Drawing" width="700px"/>

### Adjusting network graphics by programming with REPL
<img src="assets/demo02.gif" alt="Drawing" width="700px"/>

### Creating network graphics by running a code
<img src="assets/demo03.gif" alt="Drawing" width="700px"/>

<br/>

:computer::keyboard::computer_mouse: [More examples](examples/gallery.md)


## Citation
To be updated...
