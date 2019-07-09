FAQ
========


#### What kind of expressions can a cell contain ?

A cell can contain any normal Python expression such as a list 
comprehension or a generator expression. However, it cannot contain statements such as

```py
for i in xrange(10): pass
```

If you want to program more complex algorithms then use the macro editor.
There, you can define functions that use arbitrary Python code and 
is callable from any cell.

Example:
Type in the macro editor:
```py
def factorize(number):
    """Silly factorizing algorithm for demonstration purposes only"""
    counter = 1
    result = []
    while counter <= number:
        if number % counter == 0:
            result.append(counter)
        counter += 1
    return result
```
And in the cell:
```py
factorize(25)
```

Result is:

`[1 5 25]`


#### What are the boundaries for the number of rows/columns/sheets ?

These are limited by your memory (and maybe your stack restriction if any). However, the 
grid is restricted to a number that changes with row size. For standard 
size (GTK), 80 000 000 rows can be displayed.

#### Is the new file-format considered stable, or will it change again ?

The new file format is stable. This means that future versions of Pyspread will be able to read the old format.

#### Can pyspread still read the old format?

Unfortunately not. If you have old `.pys` files, install both versions of pyspread and 
copy the cell contents via the Clipboard from the old to the new version. However, cell 
formatting cannot be preserved this way.

