// Coin ICO
pragma solidity =0.8.19;

contract ico {

    // Max number of coins available for sale
    uint public maxCoins = 1000000;

    // The usd to coins conversion rate
    uint public usd_to_coins = 1000;

    // total numb of coins bought by investors
    uint public total_coins_bought = 0;

    // Mapping from the investor address to its equity in coins and usd
    mapping(address => uint) equity_coins;
    mapping(address => uint) equity_usd;

    // Check if an investor is able buy coins
    modifier can_buy_coins(uint usd_invested) {
        require(usd_invested * usd_to_coins + total_coins_bought <= maxCoins);
        _;
    }

    // gettig the equity in coins of an investor
    function equity_in_coins(address investor) external view returns (uint) {
        return equity_coins[investor];

    // Buying coins
    function buy_coins(address investor, uint usd_invested) external 
        can_buy_coins(usd_invested) {
        uint coins_bought = usd_invested * usd_to_coins;
        equity_coins[investor] += coins_bought;
        equity_usd[investor] = equity_coins[investor] / usd_to_coins;
        total_coins_bought += coins_bought;

    }

    // Selling coins
    function sell_coins(address investor, uint coins_sold) external {
        equity_coins[investor] -= coins_sold;
        equity_usd[investor] = equity_coins[investor] / usd_to_coins;
        total_coins_bought -= coins_sold;
    }


}