import subdivx
t = subdivx.search("the terror")
t = subdivx.search("the terror s01")
t = subdivx.search("the terror s01e01")
t = subdivx.search("this fucking tv show don't exist even if she wants")
t = subdivx.search("the terror s01e01")
s = t[0]
for n in s.__dict__:
    print(n, getattr(s, n))
# s.get_subtitle()
