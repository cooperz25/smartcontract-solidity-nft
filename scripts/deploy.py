from msilib.schema import File
import re
from sys import meta_path
from winreg import HKEY_LOCAL_MACHINE
from scripts import helper
from brownie import BasicNFT, AdvancedNFT, config, network
import time
from pathlib import Path
from metadata import MetaDataTemplate
from datetime import date
import json, requests
import os

DEMO_URI = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def deployNFTBasic():
    acc = helper.getAccount()
    basicNFT = BasicNFT.deploy({"from": acc})
    tx = basicNFT.mintNFT(acc)
    tx.wait(1)

    print(
        f"Awesome, you can view your NFT at {OPENSEA_URL.format(basicNFT.address, basicNFT.getLastestTokenId())}"
    )


def deployNFTAdvanced():
    acc = helper.getAccount()
    advancedNFT = AdvancedNFT.deploy(
        config["networks"][network.show_active()]["vrf_cord_contract"],
        config["networks"][network.show_active()]["link_token"],
        config["networks"][network.show_active()]["key_hash"],
        config["networks"][network.show_active()]["fee"],
        {"from": acc},
        publish_source=False,
    )


def main():
    # deployNFTBasic()
    deployNFTAdvanced()
    mintNewNFT(3)


def mintNewNFT(amount):

    acc = helper.getAccount()
    advancedNFT = AdvancedNFT[-1]

    fee = config["networks"][network.show_active()]["fee"]
    helper.fundContract(advancedNFT, fee * amount)

    for i in range(amount):

        # mint
        tx = advancedNFT.mintNFT(acc, {"from": acc})
        tx.wait(1)

        # set  URI
        tokenId = advancedNFT.getLastestTokenId() - 1
        print("token id ", tokenId)
        print(f"tokenIdToClass {advancedNFT.tokenIdToClass(tokenId)}")

        setMetadata(advancedNFT.tokenIdToClass(tokenId), advancedNFT, tokenId, acc)

        # done
        print(
            f"Awesome, you can view your NFT at {OPENSEA_URL.format(advancedNFT.address, tokenId)}"
        )
        print(f"random {advancedNFT.randomResult()}")


def setMetadata(classIdx, advancedNFT, tokenId, acc):
    className = helper.getClassName(classIdx)
    networkName = helper.getNetWorkName()
    metadata = MetaDataTemplate.METADATA_TEMPLATE
    metaLinkFilePath = f"./metadata/metadata_links.json"
    metadataFilePath = f"./metadata/{networkName}/{className}.json"

    metaLink = getMetaLink(metaLinkFilePath, className)

    if len(metaLink) > 0:
        print("The metadata of this class has been already set")
        print(f"Setting URI for {className}-{tokenId}")
        # read metadata from json file
        setUriForToken(advancedNFT, tokenId, metaLink, acc)

    else:
        # upload imgs to ipfs and get the link
        print(f"Uploading img for {className}")
        imgFilePath = f"./img/{className}.jpg"
        image_uri = uploadFileToIPFS(imgFilePath)

        # store link and other metadata to a json obj
        metadata["name"] = f"{className}-{tokenId}"
        metadata["image"] = image_uri

        saveToFile(metadataFilePath, metadata)
        metadataUri = uploadFileToIPFS(metadataFilePath)
        updateNewLink(metaLinkFilePath, className, metadataUri)

        # update it to smart contract
        print(f"Setting metadata for {className}")
        setUriForToken(advancedNFT, tokenId, metadataUri, acc)


def updateNewLink(metaLinkFilePath, className, metadataUri):
    with Path(metaLinkFilePath).open("r+") as f:
        links = json.load(f)
        links[className] = metadataUri
    with Path(metaLinkFilePath).open("w+") as f:
        json.dump(links, f)


def saveToFile(filePath, data):
    with Path(filePath).open("w") as f:
        json.dump(data, f)


def getMetaLink(metadataFilePath, className):
    if os.path.exists(metadataFilePath):
        # read the json file to find link
        f = open(metadataFilePath)
        metaLinks = json.load(f)
        if className in metaLinks:
            link = metaLinks[className]
            return link
        else:
            return ""
    else:
        return ""


def setUriForToken(advancedNFT, tokenId, uri, acc):
    advancedNFT.setTokenURI(tokenId, uri, {"from": acc})


def uploadFileToIPFS(filePath):
    with Path(filePath).open("rb") as f:
        file = f.read()
        BASE_URL = "http://127.0.0.1:5001"
        endPoint = "/api/v0/add"

        res = requests.post(url=f"{BASE_URL}{endPoint}", files={"file": file})
        hash = res.json()["Hash"]

        fileName = filePath.split("/")[-1]
        image_uri = f"https://ipfs.io/ipfs/{hash}?filename={fileName}"

        print(f"uploaded uri {image_uri}")
        return image_uri
