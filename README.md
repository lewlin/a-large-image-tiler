# 96-well plates image cropper

This is a utility that I wrote to help me with my work. 


Simple graphical interface which allows a user to draw grids of variable 
size. Grids dynamically follow mouse cursor as being placed, can be 
dragged by the edges and rotated by the corners. Dynamical resizing is 
also possible (by clicking on the little square). 

This script is part of an interface of a more complex  software that I am
 currently writing. The software aims to automatically count microbial 
 colonies from 
 images obtained by spotting a 96-well plate  (commonly used in microbiology
  wet lab). Hence,
 the default grid size is 12 x 8.  

You can adapt the `MovableGrid` class to your software, which provides an object
addable to a `QGraphicsScene`. In order to work, the four mouse handler virtual 
functions of the corresponding `QGraphicsView` needs to be reimplemented in 
a similar way I have done here.

Enjoy!

## Screenshot
![alt text][screenshot]

[screenshot]: https://github.com/Llewlyn/Adjustable-12-x-8-grid/blob/master/screenshot.png "Screenshot"

