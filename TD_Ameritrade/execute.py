import concurrent.futures, time, pandas as pd, math
from equity_momentum_strat import build_mom_list
from moving_avg import trend_filter
from td_api import trade, get_price, auth, get_account_info
pd.set_option('mode.chained_assignment', None)

break_str = '#' * 100

def target_weight(iterable):
    #print(iterable)
    ticker, instruction, quantity, access_token = iterable.split(",")
    trade(instruction, ticker, quantity, access_token)
    print(str(instruction) + " " + str(quantity) + " " + str(ticker))
    return 'Done ...'

def run_system(equity_positons, cash_available_to_trade, total_equity, access_token):
    print(equity_positons)
    bond_symbol = "TLT"
    #Check bull or bear market
    current_trend = trend_filter()

    print(current_trend)

    ML, inv_vola_table = build_mom_list()

    df_mom_list = pd.DataFrame(data=ML)
    df_mom_list.index.name = 'Symbol'
    df_mom_list.columns = ['r2']
    #print(df_mom_list)

    df_weight = pd.DataFrame(data=inv_vola_table)
    df_weight.index.name = 'Symbol'
    df_weight.columns = ['Weight']
    #print(df_weight)

    final_buy_list = df_mom_list.merge(df_weight, left_index=True, right_index=True) \
        .rename(columns={'0_y': 'Weight', '0_x': 'r2'}).reset_index()

    print(final_buy_list)#, current_trend)

    print("Cash = "+ str(cash_available_to_trade))
    print("Equity to Trade = " + str(total_equity))

    final_buy_list.to_csv("final_buy_list.csv")

    current_trend = "BULL"

    if current_trend == "BEAR":
        final_buy_list = final_buy_list[-1:]
    elif current_trend == "BULL":
        final_buy_list = final_buy_list

    # NOT CURRENTLY USING A DO NOT SELL LIST BECAUSE WANT TO DROP ALL STOCKS IN A BEAR MARKET
    do_not_sell = []
    print(final_buy_list)

    # Get current list of positions
    equity_positons.rename(columns={"symbol": "Symbol"}, inplace=True)
    #equity_positons["Symbol"] = equity_positons["Symbol"].replace(["ZG"],"Z")

    rebalance_full_sell = equity_positons[~equity_positons.Symbol.isin(final_buy_list["Symbol"])]
    #rebalance_full_sell["longQuantity"] = int(rebalance_full_sell["longQuantity"])

    rebalance_new_buy = final_buy_list[~final_buy_list.Symbol.isin(equity_positons["Symbol"])]
    rebalance_new_buy["TargetMarketValue"] = rebalance_new_buy["Weight"] * total_equity
    rebalance_new_buy["Current Price"] = rebalance_new_buy["Symbol"].apply(get_price)
    rebalance_new_buy["Quantity"] = (rebalance_new_buy["TargetMarketValue"] / rebalance_new_buy["Current Price"])
    rebalance_new_buy["Quantity"] = rebalance_new_buy["Quantity"].apply(lambda x: math.floor(float(x)))

    #print(rebalance_full_sell)
    #print(rebalance_new_buy)

    full_sell_iterable = rebalance_full_sell["Symbol"].astype(str)+",Sell,"+rebalance_full_sell["longQuantity"].astype(str)+","+access_token
    new_buy_iterable = rebalance_new_buy["Symbol"].astype(str)+",Buy,"+rebalance_new_buy["Quantity"].astype(str)+","+access_token

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(target_weight, full_sell_iterable)

    equity_positons = equity_positons.merge(final_buy_list, on="Symbol")

    equity_positons["TargetMarketValue"] = equity_positons["Weight"] * total_equity
    equity_positons["Difference"] = equity_positons["TargetMarketValue"] - equity_positons["marketValue"]
    equity_positons["Action"] = equity_positons['Difference'].apply(lambda x: "Sell" if x < 0 else "Buy")
    equity_positons["Current Price"] = equity_positons["Symbol"].apply(get_price)
    equity_positons["Quantity"] = (equity_positons["Difference"]/equity_positons["Current Price"])
    equity_positons["Quantity"] = equity_positons["Quantity"].apply(lambda x: math.floor(float(x)))
    equity_positons["absQuantity"] = equity_positons["Quantity"].abs()
    #print(equity_positons)
    indexNames = equity_positons[equity_positons['absQuantity'] == 0].index
    equity_positons.drop(indexNames, inplace=True)

    #print(equity_positons)

    target_iterable = equity_positons["Symbol"].astype(str)+","+equity_positons["Action"].astype(str)+","+equity_positons["absQuantity"].astype(str)+","+access_token
    #print(target_iterable)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(target_weight, target_iterable)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(target_weight, new_buy_iterable)

def td_interact():
    print("Authenticating Trading API")
    access_token = auth()
    print("Success! :) ")

    print("\n" + break_str + "\n")

    current_positions, cash_available_to_trade, total_equity = get_account_info(access_token)

    cash_available_to_trade = float(cash_available_to_trade)

    total_equity = (float(total_equity) - 20000)*.25

    if current_positions.empty:
        equity_positons = pd.DataFrame([])
    else:
        equity_positons = current_positions[current_positions['assetType'].isin(['EQUITY'])]

    #equity_positons = equity_positons[equity_positons.symbol != "MSTR"]
    #equity_positons = equity_positons[equity_positons.symbol != "MARA"]
    #equity_positons = equity_positons[equity_positons.symbol != "COIN"]

    return equity_positons, cash_available_to_trade, total_equity, access_token

if __name__ == '__main__':
    start = time.perf_counter()
    #get current positions and cash
    equity_positons, cash_available_to_trade, total_equity, access_token = td_interact()

    #run the system
    run_system(equity_positons, cash_available_to_trade, total_equity, access_token)

    finish = time.perf_counter()

    print(f'Finished in {round(finish-start, 2)} second(s)')