
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trie import Trie

trie = Trie()

trie.insert("Ameerpet")
trie.insert("Ameerpet East")
trie.insert("Miyapur")
trie.insert("Moosapet")

print("Suggestions for 'ame':", trie.search_prefix("ame"))
print("Suggestions for 'M':", trie.search_prefix("M"))

assert "Ameerpet" in trie.search_prefix("ame")
assert "Miyapur" in trie.search_prefix("m")
assert trie.search_prefix("xyz") == []

assert trie.remove("Ameerpet")
assert "Ameerpet" not in trie.search_prefix("ame")

print("Trie tests passed!")
