from __future__ import annotations


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LinkedHashMap:
    """A dict whose iteration order can be insertion-order or access-order.

    When *access_order* is False (the default), keys iterate in insertion
    order. Reassigning an existing key keeps its original position.

    When *access_order* is True, every read or write of an existing key moves
    that key to the end, giving least-recently-used iteration semantics.

    Backed by a doubly-linked list plus a dict, giving O(1) lookups and
    O(1) order changes. No third-party dependencies.
    """

    def __init__(self, access_order=False):
        self._dict = {}
        self._access_order = access_order
        self._head = _Node(None, None)
        self._tail = _Node(None, None)
        self._head.next = self._tail
        self._tail.prev = self._head

    def __setitem__(self, key, value):
        node = self._dict.get(key)
        if node is None:
            node = _Node(key, value)
            self._dict[key] = node
            self._append(node)
        else:
            node.value = value
            if self._access_order:
                self._move_to_end(node)

    def __getitem__(self, key):
        node = self._dict[key]
        if self._access_order:
            self._move_to_end(node)
        return node.value

    def __delitem__(self, key):
        node = self._dict.pop(key)
        self._unlink(node)

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        node = self._head.next
        while node is not self._tail:
            yield node.key
            node = node.next

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return "LinkedHashMap({!r})".format(list(self.items()))

    def get(self, key, default=None):
        """Return *value* for *key*, or *default* if absent.

        Counts as an access only when the key is present and access_order is
        True. Mirrors dict.get, so a missing key never raises and never
        reorders anything.
        """
        node = self._dict.get(key)
        if node is None:
            return default
        if self._access_order:
            self._move_to_end(node)
        return node.value

    def pop(self, key, default=__import__("builtins").object):
        """Remove and return the value for *key*.

        If *key* is absent, return *default* when given, else raise KeyError.
        The sentinel default is a unique object so callers can distinguish
        "default not supplied" from "caller passed None".
        """
        node = self._dict.get(key)
        if node is None:
            if default is __import__("builtins").object:
                raise KeyError(key)
            return default
        del self[key]
        return node.value

    def popitem(self, last=True):
        """Remove and return a (key, value) pair.

        By default removes the most-recently-inserted (or accessed) entry.
        Pass last=False to pop the least-recently-inserted entry instead.
        Raises KeyError if empty.
        """
        if not self._dict:
            raise KeyError("popitem(): LinkedHashMap is empty")
        if last:
            node = self._tail.prev
        else:
            node = self._head.next
        del self[node.key]
        return (node.key, node.value)

    def keys(self):
        return list(self.__iter__())

    def values(self):
        return [self._dict[k].value for k in self]

    def items(self):
        return [(k, self._dict[k].value) for k in self]

    def update(self, other=(), **kwargs):
        if isinstance(other, (LinkedHashMap, dict)):
            other = other.items()
        for k, v in other:
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v
        return self

    def setdefault(self, key, default=None):
        node = self._dict.get(key)
        if node is None:
            self[key] = default
            return default
        return node.value

    def copy(self):
        clone = LinkedHashMap(access_order=self._access_order)
        clone.update(self.items())
        return clone

    def clear(self):
        self._dict.clear()
        self._head.next = self._tail
        self._tail.prev = self._head

    def move_to_end(self, key, last=True):
        """Move an existing *key* to the end (or start when last=False)."""
        node = self._dict[key]
        if last:
            self._move_to_end(node)
        else:
            self._move_to_front(node)

    def _append(self, node):
        prev = self._tail.prev
        prev.next = node
        node.prev = prev
        node.next = self._tail
        self._tail.prev = node

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    def _move_to_end(self, node):
        if node.next is self._tail:
            return
        self._unlink(node)
        self._append(node)

    def _move_to_front(self, node):
        if node.prev is self._head:
            return
        self._unlink(node)
        first = self._head.next
        self._head.next = node
        node.prev = self._head
        node.next = first
        first.prev = node
