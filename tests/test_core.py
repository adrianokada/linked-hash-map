import unittest

from linked_hash_map import LinkedHashMap


class TestInsertionOrder(unittest.TestCase):
    def test_insertion_order_preserved(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        self.assertEqual(list(m), ["a", "b", "c"])
        self.assertEqual(list(m.keys()), ["a", "b", "c"])
        self.assertEqual(list(m.values()), [1, 2, 3])
        self.assertEqual(list(m.items()), [("a", 1), ("b", 2), ("c", 3)])

    def test_reassign_keeps_position(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        m["a"] = 10
        self.assertEqual(list(m), ["a", "b", "c"])
        self.assertEqual(list(m.values()), [10, 2, 3])


class TestAccessOrder(unittest.TestCase):
    def test_get_reorders(self):
        m = LinkedHashMap(access_order=True)
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        self.assertEqual(m["a"], 1)
        self.assertEqual(list(m), ["b", "c", "a"])

    def test_setitem_existing_reorders(self):
        m = LinkedHashMap(access_order=True)
        m["a"] = 1
        m["b"] = 2
        m["a"] = 10
        self.assertEqual(list(m), ["b", "a"])
        self.assertEqual(m["a"], 10)

    def test_get_missing_key_no_reorder(self):
        m = LinkedHashMap(access_order=True)
        m["a"] = 1
        m["b"] = 2
        self.assertIsNone(m.get("z"))
        self.assertEqual(list(m), ["a", "b"])


class TestDel(unittest.TestCase):
    def test_delitem(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        del m["b"]
        self.assertEqual(list(m), ["a", "c"])

    def test_delitem_missing_raises(self):
        m = LinkedHashMap()
        with self.assertRaises(KeyError):
            del m["x"]


class TestPop(unittest.TestCase):
    def test_pop_default(self):
        m = LinkedHashMap()
        m["a"] = 1
        self.assertEqual(m.pop("z", 42), 42)
        self.assertEqual(list(m), ["a"])

    def test_pop_missing_raises(self):
        m = LinkedHashMap()
        with self.assertRaises(KeyError):
            m.pop("z")

    def test_pop_explicit_none(self):
        m = LinkedHashMap()
        self.assertIsNone(m.pop("z", None))

    def test_popitem_last(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        self.assertEqual(m.popitem(last=True), ("c", 3))
        self.assertEqual(list(m), ["a", "b"])

    def test_popitem_first(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        self.assertEqual(m.popitem(last=False), ("a", 1))
        self.assertEqual(list(m), ["b", "c"])

    def test_popitem_empty_raises(self):
        m = LinkedHashMap()
        with self.assertRaises(KeyError):
            m.popitem()


class TestUpdate(unittest.TestCase):
    def test_update_pairs(self):
        m = LinkedHashMap()
        m.update([("a", 1), ("b", 2)])
        self.assertEqual(list(m.items()), [("a", 1), ("b", 2)])

    def test_update_kwargs(self):
        m = LinkedHashMap()
        m.update({"a": 1}, b=2)
        self.assertEqual(list(m.items()), [("a", 1), ("b", 2)])

    def test_update_pairs_reorders_access_order(self):
        m = LinkedHashMap(access_order=True)
        m["a"] = 1
        m["b"] = 2
        m.update({"a": 99})
        self.assertEqual(list(m), ["b", "a"])


class TestSetdefault(unittest.TestCase):
    def test_setdefault_existing_no_change(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        self.assertEqual(m.setdefault("a", 99), 1)
        self.assertEqual(list(m), ["a", "b"])

    def test_setdefault_missing_appends(self):
        m = LinkedHashMap()
        m["a"] = 1
        self.assertEqual(m.setdefault("b", 2), 2)
        self.assertEqual(list(m), ["a", "b"])


class TestCopyClear(unittest.TestCase):
    def test_copy_preserves_order(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        c = m.copy()
        self.assertEqual(list(c), ["a", "b"])
        c["c"] = 3
        self.assertEqual(list(m), ["a", "b"])

    def test_clear(self):
        m = LinkedHashMap()
        m["a"] = 1
        m.clear()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m), [])
        m["a"] = 1
        self.assertEqual(list(m), ["a"])


class TestMoveToPos(unittest.TestCase):
    def test_move_to_end(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        m.move_to_end("a")
        self.assertEqual(list(m), ["b", "c", "a"])

    def test_move_to_end_already_last(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m.move_to_end("b")
        self.assertEqual(list(m), ["a", "b"])

    def test_move_to_front(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        m.move_to_end("c", last=False)
        self.assertEqual(list(m), ["c", "a", "b"])

    def test_move_to_front_already_first(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m.move_to_end("a", last=False)
        self.assertEqual(list(m), ["a", "b"])

    def test_move_missing_raises(self):
        m = LinkedHashMap()
        m["a"] = 1
        with self.assertRaises(KeyError):
            m.move_to_end("x")


class TestContains(unittest.TestCase):
    def test_contains(self):
        m = LinkedHashMap()
        m["a"] = 1
        self.assertIn("a", m)
        self.assertNotIn("b", m)

    def test_contains_no_reorder(self):
        m = LinkedHashMap(access_order=True)
        m["a"] = 1
        m["b"] = 2
        _ = "a" in m
        self.assertEqual(list(m), ["a", "b"])


class TestMisc(unittest.TestCase):
    def test_len(self):
        m = LinkedHashMap()
        self.assertEqual(len(m), 0)
        m["a"] = 1
        m["b"] = 2
        self.assertEqual(len(m), 2)

    def test_repr_evaluable(self):
        m = LinkedHashMap()
        m["a"] = 1
        self.assertEqual(repr(m), "LinkedHashMap([('a', 1)])")

    def test_pop_preserves_order(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["c"] = 3
        self.assertEqual(m.pop("b"), 2)
        self.assertEqual(list(m), ["a", "c"])


if __name__ == "__main__":
    unittest.main()
