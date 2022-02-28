# DuMAF_DuTween
Duduf Tweener for Maya

DuTween is a *Tween Machine* for *Autodesk Maya* working with all versions of *Maya*, in either *Python 2* or *Python 3*. It is very simple and focuses on ease of use and performance.

## Install

- Copy `DuTween.py` to a *plug-ins* folder in Maya. It can be in the installation folder of Maya for all users, or simply in the `maya` subdirectory of your documents.  
e.g. on Windows: `C:\users\yourName\documents\maya\plug-ins`.

- Restart *Maya* if it was running.

- Enable the plugin via `Windows ► Settings/Preferences ► Plug-in Manager`.

## Use

Tweening is available via a *Maya command* which you can add to any shelf, or assign a shorcut. You can also simply open and run the script without installation.

![](https://github.com/RxLaboratory/DuMAF_DuTween/blob/main/dutween.png)  
An icon `dutween.png` is provided to be used in shelves if you wish.

The command is `dutween`.

When used without parameters, it shows a simple user interface with a slider and a value to tween the selected objects.

```py
# Python
import maya.cmds as cmds
cmds.dutween()
```

```mel
// Mel
dutween
```

![](https://github.com/RxLaboratory/DuMAF_DuTween/blob/main/dutween_screenshot.png)

You can also use some parameters to automatically add a keyframe without showing the interface, for example to use it in your own scripts, or to add buttons with predefined values in a shelf.

- `ratio` or `r`: a value in the range `[0.0, 1.0]`. Sets the tweening ratio.

```py
# Python
import maya.cmds as cmds
cmds.dutween(r=0.75)
```

```mel
// Mel
dutween -r 0.75
```
