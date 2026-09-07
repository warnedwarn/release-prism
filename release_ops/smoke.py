import json, re, time
from pathlib import Path
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionStatus

ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text()
DEPLOYMENT = json.loads((ROOT / "evidence/deployment.json").read_text())

def value(name):
    return re.search(rf'^{name}\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()

account = create_account(account_private_key=value("ACCOUNT_2_GENLAYER_PRIVATE_KEY"))
client = create_client(chain=studionet, account=account)
contract = DEPLOYMENT["contract"]
commit = DEPLOYMENT["sourceCommit"]
candidate = f"RP-{int(time.time())}"
sources = [
    f"https://raw.githubusercontent.com/warnedwarn/release-prism/{commit}/evidence/release.txt",
    f"https://cdn.jsdelivr.net/gh/warnedwarn/release-prism@{commit}/evidence/tests.txt",
    f"https://github.com/warnedwarn/release-prism/raw/{commit}/evidence/security.txt",
]

def send(name, args):
    tx = client.write_contract(address=contract, function_name=name, args=args)
    print(name, tx, flush=True)
    client.wait_for_transaction_receipt(transaction_hash=tx, status=TransactionStatus.ACCEPTED, retries=120, interval=10000)
    info = client.get_transaction(transaction_hash=tx)
    if info.get("status_name") != "ACCEPTED" or info.get("tx_execution_result_name") not in ("SUCCESS", None):
        raise RuntimeError(info)
    return tx

transactions = {
    "nominate": send("nominate", [candidate, "2.4.0", sources, int(time.time()) + 1800]),
    "assess": send("assess", [candidate]),
}
state = client.read_contract(address=contract, function_name="get_candidate", args=[candidate])
if state["state"] != "PROMOTED" or state["release"] != "2.4.0" or len(state["digests"]) != 3:
    raise RuntimeError(state)
(ROOT / "evidence/network-run.json").write_text(json.dumps({"id": candidate, "contract": contract, "sourceCommit": commit, "transactions": transactions, "state": state}, indent=2))
print(json.dumps(state, indent=2), flush=True)
