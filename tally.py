import collections
from sys import argv

names = ['random', 'modified', 'aggressive', 'expectimax', 'liar', 'oracle']
averages = collections.Counter()
for i0, n0 in enumerate(names):
  for i1, n1 in enumerate(names):
    if i0 < i1:
      output = open('score-count-%s-%s.txt' % (n0, n1), 'r')
      x= dict(collections.Counter(output.read().split()))
      total = sum(x.values())
      for y in x:
        x[y] = float(x[y])  /total
      print('0: %s, 1: %s' % (n0, n1))
      print(x, '(%d)' % total)
      averages[n0] += x['0'] if '0' in x else 0
      averages[n1] += x['1'] if '1' in x else 0
      output.close()

for c in averages:
  averages[c]/= len(names) - 1

print(averages)