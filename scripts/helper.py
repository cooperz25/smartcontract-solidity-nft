from brownie import accounts, network, config, Contract, LinkToken


DEV_NETWORK = ["development", "gananche-local"]
MAINNET_FORK = ["mainnet-fork-dev", "mainnet-fork-dev2"]
CLASS_NAME = ["WEAK", "NORMAL", "STRONG", "SUPER", "GOD"]


def getAccount(index=None, networkId=None):
    if network.show_active() in DEV_NETWORK or network.show_active() in MAINNET_FORK:
        if index:
            return accounts[index]
        if networkId:
            return accounts.load(networkId)
        return accounts[0]

    # default
    return accounts.add(config["wallets"]["key"])


def fundContract(targetContract, value):

    contract_address = config["networks"][network.show_active()]["link_token"]
    linkContract = Contract.from_abi(LinkToken._name, contract_address, LinkToken.abi)
    linkContract.transfer(targetContract, value, {"from": getAccount()}).wait(1)


def getClassName(tokenId):
    return CLASS_NAME[tokenId]


def getNetWorkName():
    return network.show_active()
