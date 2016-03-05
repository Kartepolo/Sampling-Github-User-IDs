import random
import numpy as np
from multiprocessing import Process, Manager
import requests
import json
from gscrawler import check_limit
all_tokens = ["1c9bc9c0e085fad91caae25398e01f38ba98119b",
              "bea5e7eba598d0fa958eafdea4c9dc58585d1731",
              "08ac8f890527c716e5ea8370499d748808086627",
              "1c9bc9c0e085fad91caae25398e01f38ba98119b",
              "42acddc62fcbc337046f56362c62c4bfe2fa4d98",
              "0da28aed2ec109c58c4d230211d4856bbe4fd595",
              "b2b4ac180bc6548a049392b4bb75648ad08617e4",
              "b2b4ac180bc6548a049392b4bb75648ad08617e4",
              "3d14d7a23483c1f42d56402d1fb6537f8059445b",

              "fb60f7f941df5627702e4bdfe5ec45af36c813d0",
              "790b5d5357b41c874372bf2e963fa815aa6dc65a",
              "669f2888681d5da48f5bec11f2ca252de7483884",
              "16813ad46416be897deb5844847c8ec1ca44ecf1",
              "91bf07d0c54b969efa38f45d3d318dff92bf9007",
              "0711bb5eb28e499a53b80d843c44c87708091e57",

              "e7b1233ca19d3af3ed0be3ab35749c7949a199c4",
              "6db8940fde1f9fecdb85c16381352df45b62c94c",
              "5344c0f21b56a4de1d8d472b931f69a07d07c716",
              "84a072d69f4a09662132edee611b393be9e5f331",
              "f4997faab1eb1d7d64b59a9c02629097db0fd468",
              "735c0d7fe7a5c33dcf82817a55a64630af8f94f8",

              "27d04ed480f7860d73e8f4c07353af57b779f7c0",
              "96c9da32feee2f52ef6b595c2c7d31ccf846a91b",
              "e1c6b9b18c64f45caf5bd8a7fca082c6813fc7fa",
              "3a5c72bfae8da08bd1fd3aa901b53477f7bcbd89",
              "aa2acb42c9b997e560bc36ac676c8171b1936dab",
              "5199b9cab81540e19babe1af7a7f40e39858be06",

              "da0a2bb408200a43a4911c2dd9c83ac14224a6e7",
              "63403eb69ba095fae50f4828d0ae2e94a6f70dda",
              "1c8b3ce366dfe15fb782fa8f246080590552c438",
              "9b0a29e14172df3b91192149e9ff3c719c983a38",
              "8a90df4674d9262556411f920da5aedb673a303d",
              "63f5dce57ae7d27ce4501098d409d8b6c4536726",
              "e343a0f8d063675f40971cc90f4fdc7f170d5421",
              "2ed091b2a12ce3b80ea46922f5bc7365626f3572",
              "c6948611f74a64d01557231e21d462bf66d5fff5",
              "5f8cb35d953a97479fc50590051373af9c099898",
              "72d1f0749545028292b7d50c30c60c39dc847249",
              "5bcd67fdac7f5dfeda164a2c9bb63ebeaaeddfc7",
              "685cf6c8ad14377a5a7420dae42246129ff22841"]

# TEST RANGE
MINID = 13200001
MAXID = 17226000
IDSPACE = MAXID- MINID + 1
# query parameters
DEF_PAGE_SIZE= 100 # 1 ~ 100
QUERY_RANGE = 100 # like 100, 200, 300, ...
STEP_SIZE = 49 # < QUERY_RANGE (not equal)
NO_RES = QUERY_RANGE-STEP_SIZE
# ground truth for 1-4400000
GT= 4129983#4260386

limit = check_limit(all_tokens)
limit.sort()


def since(uid, maxid = MAXID, per_page = DEF_PAGE_SIZE):
    token = all_tokens[0]
    url = "https://api.github.com/users?since=" + str(uid-1) + "&access_token=" + token + "&&per_page=" + str(
            per_page)
    req = requests.get(url)
    if req.status_code == 403:
            all_tokens.pop(0)
            if not all_tokens:
                raise Exception("tokens exceeded the limit")
            else:
                return since(uid, per_page)
    res = json.loads(req.content)
    li = [i['id'] for i in res if i['id']<=MAXID]