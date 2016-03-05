import json, requests, os, pickle, time, re, numpy, traceback
from multiprocessing import Process

# set multiple tokens and ID range
all_tokens = ["620b2ebfbe97c8d2f3f7eef92b343700f0957059",
              "e343a0f8d063675f40971cc90f4fdc7f170d5421",
              "2ed091b2a12ce3b80ea46922f5bc7365626f3572",
              "c6948611f74a64d01557231e21d462bf66d5fff5",
              "5f8cb35d953a97479fc50590051373af9c099898",
              "72d1f0749545028292b7d50c30c60c39dc847249",
              "5bcd67fdac7f5dfeda164a2c9bb63ebeaaeddfc7",
              "685cf6c8ad14377a5a7420dae42246129ff22841"]  #
STARTID = 13200001
ENDID = 17226000  # each retrieves 4.4 M and ENDID must be divisible by 1000
NO_TOKEN = 2

DEF_FILE_SIZE = 1000
MAXID = 17210209
DEF_PAGE = 100


def findMax(upper, lower=1, token=all_tokens[0]):
    def minmax(uid):
        url = "https://api.github.com/users?since=" + str(uid) + "&access_token=" + token + "&&per_page=100"
        l = len(json.loads(requests.get(url).content))
        return l

    if upper <= lower or minmax(upper) > 0 or minmax(lower) == 0:
        return None
    if upper - lower == 1:
        return lower
    else:
        sep = (upper + lower) / 2
        return findMax(upper, sep) or findMax(sep, lower)


def check_limit(tokens):
    res = []
    for token in tokens:
        url = "https://api.github.com/rate_limit?access_token=" + token
        res.append(json.loads(requests.get(url).content)['rate']['remaining'])
    return res


def checkFile(shares):
    if not hasattr(shares, '__iter__'):
        shares = [shares]
    for share_id in shares:
        with open("data/%05dX" % share_id, "rb") as f:
            r = pickle.load(f)
            print "data/%05dX - %7d - %7d -%6d" % (share_id, r[0]['id'], r[-1]['id'], len(r))


class Scrawls():
    def __init__(self, shares, tokens):
        # inclusive start and end
        self.tokens = tokens
        self.shares = shares

    def since(self, uid, per_page=DEF_PAGE):
        token = self.tokens[0]
        url = "https://api.github.com/users?since=" + str(uid) + "&access_token=" + token + "&&per_page=" + str(
            per_page)
        req = requests.get(url)
        if req.status_code == 403:
            self.tokens.pop(0)
            if not self.tokens:
                raise Exception("tokens exceeded the limit")
            else:
                return Scrawls.since(self, uid)
        res = json.loads(req.content)
        return res, res[-1]['id']

    def retrieve(self, share_id, share_size):
        # for example, get since(0, per_page=1)+ ... +since(999, per_page=1)
        uid = (share_id - 1) * share_size
        end = share_id * share_size
        res = []
        delay = []
        while uid < end:
            tmp, uid = Scrawls.since(self, uid)
            res += delay
            delay = tmp
        else:
            if not delay: return res
            while delay[-1]['id'] > end:
                delay.pop()
                if not delay: break
            res += delay
        return res

    def scrw(self, share_size=DEF_FILE_SIZE):
        for i in self.shares:
            share = i
            if not os.path.exists("data/%05dX" % share):
                try:
                    res = Scrawls.retrieve(self, share, share_size)
                except Exception as e:
                    print e
                    traceback.print_exc()
                    return
                with open("data/%05dO" % share, "wb") as f:
                    pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)
                    os.rename("data/%05dO" % share, "data/%05dX" % share)


def merge_result(start, end, output_name="data/_merged"):
    res = []
    for share in range(start, end + 1):
        with open("data/%05dX" % share, "rb") as f:
            res += pickle.load(f)
    with open(output_name, "wb") as f:
        pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)


def monitor():
    last = 0
    while True:
        remaining = check_limit(all_tokens)
        if all(numpy.array(last) == numpy.array(remaining)):
            return
        print remaining
        last = remaining
        time.sleep(3)


def main(ntoken, max_avg_job_num=None):
    nthread = len(all_tokens) / ntoken
    done = set([int(j.group())
                for j in [re.search(r'\d{5}(?=X)', i)
                          for i in os.listdir("./data")]
                if j])
    unfinished = list(set(range((STARTID - 1)/ DEF_FILE_SIZE + 1, ENDID / DEF_FILE_SIZE + 1)) - done)
    maxi = len(unfinished)
    if maxi==0:
        print "ALL SET"
        return
    avg_job_number = max_avg_job_num or maxi/nthread + 1
    q = []
    for i in xrange(nthread):
        scrawl = Scrawls(unfinished[min([i * avg_job_number, maxi]):min([(i + 1) * avg_job_number, maxi])],
                         all_tokens[i * ntoken:(i + 1) * ntoken])
        p = Process(target=scrawl.scrw)
        p.start()
        q.append(p)

    p = Process(target=monitor)
    p.start()
    p.join()
    for i in q:
        i.join()
    print "assigned work done, restart to check if any unfinished"


def shell():
    print "Remaining times for each token: ",
    print check_limit(all_tokens)
    print "Your setting: ID range [%s, %s]\nThe number of tokens for each thread: %d" % (STARTID, ENDID, NO_TOKEN)

    while True:
        strs = raw_input()
        strli = strs.lower().strip().split()
        if strli[0] == 'q':
            return
        elif strli[0] in ['s', "scrawl"]:
            main(NO_TOKEN)
        elif strli[0] in ['c', "check"]:
            if strli[1] in ['f', "file"]:
                checkFile([int(j.group()) for j in [re.search(r'\d{5}(?=X)', i) for i in os.listdir("./data")] if j])
            elif strli[1] in ['t', "times"]:
                print check_limit(all_tokens)
            elif strli[1] in ['r', "rest"]:
                done = set([int(j.group()) for j in [re.search(r'\d{5}(?=X)', i) for i in os.listdir("./data")] if j])
                unfinished = list(set(range((STARTID - 1) / DEF_FILE_SIZE, ENDID / DEF_FILE_SIZE)) - done)
                print "unfinished shares:", len(unfinished), 1.0 * len(unfinished) / (ENDID - STARTID) * DEF_FILE_SIZE
            else:
                print "unknown command"
        elif strli[0] == "findmax":
            rng = 2000000
            lower = 17000000
            maxid = findMax(rng + lower, lower)
            while not maxid:
                rng *= 2
                maxid = findMax(rng + lower, lower)
            else:
                print "MAX ID:", maxid
        elif strli[0] == "admin":
            pw = raw_input("passcode")
            if pw == "passcode":
                while True:
                    cmd = raw_input()
                    if cmd == 'exit':
                        break
                    exec cmd
        elif strli[0] == "help":
            print "q: \t\tquit" \
                  "\nfindmax: \tfind max id" \
                  "\ncheck times: \tcheck remaining time for each tokens" \
                  "\ncheck file: \tcheck id range and valid id number" \
                  "\nscrawl: \tscrawl data"
        else:
            print "Unknown command"


if __name__ == "__main__":
    shell()
