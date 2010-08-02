#!/usr/bin/env python
"""Arena class"""

class Arena(object):

    """Represent a 2D arena whose coord spaces are stackable"""

    def __init__(self, cols, rows):
        """Create the data structure"""
        self.cols = cols
        self.rows = rows
        self.data = [[] for _ in xrange(rows*cols)]

    def sanity(self, coords):
        """Ensure that coords are within sane limits"""
        x, y = coords
        if not (0 <= x < self.cols) or not (0 <= y < self.rows):
            raise IndexError("Coords (%d, %d) are not valid: must be in range (0, 0) to (%d, %d)" % (x, y, self.cols-1, self.rows-1))

    def _get_list(self, coords):
        """The 2D -> 1D convertermatron"""
        self.sanity(coords)
        x, y = coords
        return self.data[x+y*self.cols]

    def coords_add(self, coords, obj):
        """Add an object by coords"""
        self._get_list(coords).append(obj)

    def coords_get_real(self, coords):
        """Get the list of objects at a set of coords"""
        return self._get_list(coords)

    def coords_get(self, coords):
        """Get a copy of the list of objects at a set of coords"""
        return self.coords_get_real(coords)[:]

    def coords_remove(self, coords, obj):
        """Remove an object by coords"""
        for i, o in enumerate(self._get_list(coords)):
            if o == obj:
                del self._get_list(coords)[i]
                return o

        raise LookupError("Did not find object")

    # TODO: maybe implement the "have" functions separately so we can use them when iterating, e.g. in GameState.spawn()

    def coords_have_obj(self, coords, obj):
        """Test for an object by coords"""
        for o in self._get_list(coords):
            if o == obj:
                return True

        return False

    def coords_have_class(self, coords, classref):
        """Test for a class by coords"""
        for o in self._get_list(coords):
            if isinstance(o, classref):
                return True

        return False

    def __iter__(self):
        """Iterate over the coords, providing x, y, list"""
        for i, l in enumerate(self.data):
            x = i % self.cols
            y = i / self.cols
            yield x, y, l
