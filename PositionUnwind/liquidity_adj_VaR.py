
'''
Liquidity Trading Risk
Chapter 24
HULL - RISK MANAGEMENT AND FINANCIAL INSTITUTIONS
'''

position = 1000000

offer_price = 2.1
bid_price = 2.0
mid_market = abs((offer_price - bid_price)/2) + bid_price

# p = dollar bid–offer spread
p = offer_price - bid_price
# s = proportional bid–offer spread for an asset
s = (offer_price - bid_price) / mid_market

liq_cost_normal = position * s / 2

liq_cost_stressed = position * s / 2

