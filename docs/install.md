
Currently, we recommend installing from the GitHub repository.
First, download a recent version of the repository.

```
git clone https://github.com/cxinsys/nezzle.git
```

Now, you can install Nezzle from the local repository.

```
cd nezzle
python setup.py install
```

If you want to easily update the most recent version of the software
from the repository, use ``develop`` option insead of ``install``.

```
python setup.py develop
```

Now, running ``git pull origin main`` is enough to update Nezzle
from the remote repository.