# linked-hash-map

A hash map that preserves insertion order of keys and, in access-order mode, moves an existing key to the end whenever it is read or reassigned — the core of an LRU cache.

```python
from linked_hash_map import LinkedHashMap

m = LinkedHashMap(access_order=True)
m["a"] = 1
m["b"] = 2
m["c"] = 3
_ = m["a"]       # "a" is now most-recently-used
print(list(m))   # ["b", "c", "a"]

m.move_to_end("b", last=False)  # move "b" to the front
print(list(m))   # ["b", "c", "a"]

print(m.popitem(last=False))    # ("b", 2), least-recently-used
```

## Why

`collections.OrderedDict` preserves insertion order but provides no access-order mode; reimplementing one by repeatedly deleting and re-inserting keys is awkward and loses the value. This library gives you a dict-like object whose iteration order is least-recently-used under reads and writes, which is the primitive an LRU cache needs. The trade-off: every entry carries two pointers, so memory per item is higher than a plain dict, and the map is not thread-safe.

## Exported names

- `LinkedHashMap(access_order=False)` — the only public class.

Methods: `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, `__len__`, `get`, `pop`, `popitem(last=True)`, `setdefault`, `update`, `copy`, `clear`, `keys`, `values`, `items`, `move_to_end(key, last=True)`.

## Edge cases

- `get` on a missing key does **not** reorder anything, even in access-order mode — a cache miss should not count as an access.
- `__contains__` never reorders; querying membership is not an access.
- `setdefault` on a missing key inserts at the end; on an existing key it returns the value without reordering, even in access-order mode (it does not go through `__getitem__`).
- `pop(key)` with no default raises `KeyError`; pass an explicit default (including `None`) to suppress the raise.
