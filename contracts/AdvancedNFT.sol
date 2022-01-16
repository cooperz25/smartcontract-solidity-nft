// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract AdvancedNFT is ERC721, VRFConsumerBase {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    mapping(uint256 => string) private _tokenURIs;

    enum CLASS {
        WEAK,
        NORMAL,
        STRONG,
        SUPER,
        GOD
    }

    mapping(bytes32 => address) public reqIdToOwner;
    event RequestIdToOwner(bytes32 reqId, address owner);
    mapping(uint256 => CLASS) public tokenIdToClass;
    event TokenIdToClass(uint256 tokenId, CLASS class);

    //vrf
    bytes32 private keyHash;
    uint256 private fee;
    uint256 public randomResult;

    constructor(
        address _vrfCoordAddr,
        address _linkTokenAddr,
        bytes32 _keyHash,
        uint256 _fee
    )
        ERC721("MonsterNFT", "MONS")
        VRFConsumerBase(
            _vrfCoordAddr, // VRF Coordinator
            _linkTokenAddr // LINK Token
        )
    {
        keyHash = _keyHash;
        fee = _fee;
    }

    function mintNFT(address player) public returns (uint256) {
        bytes32 reqId = getRandomNumber();
        reqIdToOwner[reqId] = player;
        fulfillRandomness2(reqId, 452215114 + _tokenIds.current());
        emit RequestIdToOwner(reqId, player);
    }

    function getRandomNumber() public returns (bytes32 requestId) {
        require(
            LINK.balanceOf(address(this)) >= fee,
            "Not enough LINK - fill contract with faucet"
        );
        bytes32 reqId = requestRandomness(keyHash, fee);
        return reqId;
    }

    function fulfillRandomness2(bytes32 requestId, uint256 randomness)
        internal
    {
        uint256 newItemId = _tokenIds.current();
        randomResult = randomness;
        uint256 classIdx = randomResult % 5;

        address player = reqIdToOwner[requestId];
        _mint(player, newItemId);

        tokenIdToClass[newItemId] = CLASS(classIdx);

        _tokenIds.increment();

        emit TokenIdToClass(newItemId, CLASS(classIdx));
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness)
        internal
        override
    {}

    function tokenURI(uint256 tokenId)
        public
        view
        virtual
        override
        returns (string memory)
    {
        require(
            _exists(tokenId),
            "ERC721URIStorage: URI query for nonexistent token"
        );

        string memory _tokenURI = _tokenURIs[tokenId];
        string memory base = _baseURI();

        // If there is no base URI, return the token URI.
        if (bytes(base).length == 0) {
            return _tokenURI;
        }
        // If both are set, concatenate the baseURI and tokenURI (via abi.encodePacked).
        if (bytes(_tokenURI).length > 0) {
            return string(abi.encodePacked(base, _tokenURI));
        }

        return super.tokenURI(tokenId);
    }

    function setTokenURI(uint256 _tokenId, string memory _tokenURI) public {
        require(
            _isApprovedOrOwner(_msgSender(), _tokenId),
            "ERC721: transfer caller is not owner nor approved"
        );
        _setTokenURI(_tokenId, _tokenURI);
    }

    function _setTokenURI(uint256 _tokenId, string memory _tokenURI)
        internal
        virtual
    {
        require(
            _exists(_tokenId),
            "ERC721URIStorage: URI set of nonexistent token"
        );
        _tokenURIs[_tokenId] = _tokenURI;
    }

    function getLastestTokenId() public view returns (uint256) {
        return _tokenIds.current();
    }
}
