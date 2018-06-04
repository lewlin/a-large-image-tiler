# ALIT - A large-image tiler

This is a utility that I wrote to help me with my work. It consists of a simple
graphical interface which allows a user to tile a (very large) image 
in a timely manner. 
Professional graphic editors possess
similar features, though I was surprised to learn that no commercial 
software really does what I need, which is the following:

- Load and tile very large TIFF images (~700 Mb) in a few seconds. 
- To easily draw, drag, and resize grids to conveniently choose the tiling pattern.
- To be able to save files following the labels of a 96-well plates 
(commonly used in biology). 

The screenshot gives you an idea of what the software accomplishes and how 
it works. Enjoy!

![alt text][screenshot]

[screenshot]: https://github.com/lewlin/grid-image-cropper/blob/master/screenshots/main.png "Screenshot"


## Installation
`ALIT` is written in `Python 3` and requires the `PyQt5` library and this 
should be everything you need. Currently, `ALIT` cannot be installed using 
`pip`, but I might distribute it as a Python package in future releases. 


## How to use

- Load the TIFF image you want to tile using the *Load TIFF button*. TIFF is
the only image type currently supported.
- To draw a grid, left-click with the mouse and move the pointer. A second 
left-click places the grid, right-click to cancel. The result will look similar 
to the following (where I omit the background image for clarity): 


![alt text][howto_1]

[howto_1]: https://github.com/lewlin/grid-image-cropper/blob/master/screenshots/howto_1.png "How To 1"

- The grid can be dragged by the edges, rotated using the circles at the corners
and resized by clicking on the little square. 
- You can also change the tiling patterns and toggle the labels using the 
*Grid control* widget.
- Once the grid suits you, click on *I like this grid*. 

![alt text][howto_2]

[howto_2]: https://github.com/lewlin/grid-image-cropper/blob/master/screenshots/howto_2.png "How To 2"

- You can now select a grid in the *Grid control* and start typing to rename it.
When you crop the image, the results will be saved in a folder named as the grid.
- If you don't like a grid you placed, delete it using the *Delete* button.
- When you feel brave enough, select a grid and press *Crop*. The grid squares
are now saved as TIFF files named as the corresponding labels. On my Mac, this 
is how it looks like for *3x3* grid:

![alt text][howto_3]

[howto_3]: https://github.com/lewlin/grid-image-cropper/blob/master/screenshots/howto_3.png "How To 3"

Enjoy!


