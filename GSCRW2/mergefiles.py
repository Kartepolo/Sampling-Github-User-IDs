from gscrawler import *
import sys

def merge_result(shares, output_name="data/_merged"):
    res = []
    for share in shares:
        print "data/%05dX" % share
        with open("data/%05dX" % share, "rb") as f:
            res += pickle.load(f)
    with open(output_name, "wb") as f:
        print "writing",output_name,"- %d - %d -%d" % (res[0]['id'], res[-1]['id'], len(res))
        sys.stdout.flush()
        pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)


files = [int(j.group()) for j in [re.search(r'\d{5}(?=X)', i) for i in os.listdir("./data")] if j]

nfile = int(raw_input("Final files number\n"))

sep = [files[0]]
for i in xrange(nfile):
    sep.append((files[-1] + 1 - files[0]) * (i + 1) / nfile + files[0])
for i in xrange(nfile):
    rng = range(sep[i], sep[i + 1])
    merge_result(rng, "data/_M%03d" % (i + 1))
