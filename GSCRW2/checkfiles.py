from gscrawler import *
import sys


def checkFile(shares, upper, lower=None):
    if not hasattr(shares, '__iter__'):
        shares = [shares]
    for share_id in shares:
        with open("data/%05dX" % share_id, "rb") as f:
            r = pickle.load(f)
            print "data/%05dX - %7d - %7d -%6d" % (share_id, r[0]['id'], r[-1]['id'], len(r))
            if len(r) <= upper:
                if not lower and len(r) >= lower:
                    print "\t* Found high missing rate *, checking ... ...",
                    sys.stdout.flush()
                    test = Scrawls(range(share_id, share_id + 1), all_tokens)
                    res = test.retrieve(test.shares[0], DEF_FILE_SIZE)
                    if len(res) == len(r):
                        print "Check pass"
                    else:
                        print "===Inconsistent result: data/%05dX===" % share_id
                        print "length of file: %d; length of query: %d" % (len(r), len(res))
                        rs = set([i["id"] for i in r])
                        ress = set([i["id"] for i in res])
                        print "file:", rs - ress, "query", ress - rs
                        return


if __name__ == "__main__":
    u = int(raw_input("upper\n "))
    l = None
    t = raw_input("lower\n ")
    if t:
        l = int(t)
    checkFile([int(j.group()) for j in [re.search(r'\d{5}(?=X)', i) for i in os.listdir("./data")] if j], u, l)
    # checkFile([163], u, l)
