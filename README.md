# gofuncyourself

Golang has this... interesting approach to exception handling where functions return a tuple of the actual result and a error (that may be nil).

This is a reimagining of the same concept applied to Python. It comes in form of a decorator:


```python
from gofuncyourself import gofunc

@gofunc
def div(x, y):
    return x / y
```

If you now call `div(16, 2)` it will return `(8, None)`, where `None`
references the fact that no error has occurred.

If you instead do something like `res, err = div(7, 0)` then `res` will be
None, and `err` will not; instead it will be a special error object that
contains the exception that was caught in `err.exception`.

Functions decorated with `gofunc` are to be called like this:

```python
res, err = div(x, y)
if err:
    ...  # handle exception
```

But wait, there's more!

----

What if you forget to check for an error? `gofuncyourself` protects you from
that, by raising the exception one second later, if you didn't do `if err:`.
The delay can be adjusted by passing a `delay` keyword argument to the decorator. For example, if you want to make sure the error is handled swiftly:

```python
@gofunc(delay=0.1)  # only wait for 100ms before raising
def div(x, y):
    return x / y
```


## Installation

    pip install gofuncyourself

## Acknowledgements

Based on an idea by [digitalarbeiter](https://github.com/digitalarbeiter)
