import numpy as np, time, pandas as pd, yaml
from scipy import stats
from build_quandl_universe import get_volume_closeadj

break_str = '#' * 100

with open('C:/Users/samla/OneDrive/Documents/GitHub/slasker1/eq_momentum.yml', 'r') as f:
    doc = yaml.safe_load(f)

momentum_window = doc['mom_win']
momentum_window2 = doc['mom_win2']
minimum_momentum = doc['min_mom']
number_of_stocks = doc['p_size']
index_id = doc['index']
index_average_window = doc['index_win']
v_win = doc['v_win']

def inv_vola_calc(ts):
    vola_window = v_win
    return ts.pct_change().rolling(vola_window).std().dropna().iloc[-1]

def slope(ts):
    x = np.arange(len(ts))
    log_ts = np.log(ts)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
    annualized_slope = (np.power(np.exp(slope), 252) - 1) * 100
    score = annualized_slope * (r_value ** 2)
    return score

def build_mom_list():
    start = time.perf_counter()

    my_input = input("Hello Sam, Welcome to Project Deep Ocean! \n" +
                     "Please enter 1 to rebuild your universe or 2 to continue: ")

    hist = []

    if my_input == "1":
        hist = get_volume_closeadj()
    elif my_input == "2":
        hist = pd.read_csv("quandl_hist.csv")
        hist = hist.set_index('date')

    print("I'm done collecting the full data universe.\n"
          +"Moving onto the final stage of your equity selection...")

    #EXLCUDING DATES COMES FROM UNIVERSE SCRIPT
    momentum_hist1 = hist[:momentum_window]
    momentum_hist2 = hist[:momentum_window2]

    momentum_list = momentum_hist1.apply(slope)
    momentum_list2 = momentum_hist2.apply(slope)

    # Combine the lists and make average
    momentum_concat = pd.concat((momentum_list, momentum_list2))
    mom_by_row = momentum_concat.groupby(momentum_concat.index)
    mom_means = mom_by_row.mean()

    # Sort the momentum list, and we've got ourselves a ranking table.
    ranking_table = mom_means.sort_values(ascending=False)

    #manual exclusion logic
    #ranking_table = ranking_table.drop("YSG")
    #ranking_table = ranking_table.drop("LB")

    ranking_table.to_csv("ranking_table.csv")

    # Get the top X stocks, based on the setting above. Slice the dictionary.
    # These are the stocks we want to buy.
    buy_list = ranking_table[:number_of_stocks]


    final_buy_list = buy_list[buy_list > minimum_momentum] # those who passed minimum slope requirement

    # Calculate inverse volatility, for position size. USE FINAL BUY LIST INSTEAD OF BUY LIST TO GET EQUITY EXPOSURE TO 100%
    vola_table = hist[final_buy_list.index].apply(inv_vola_calc)

    inv_vola_table = 1 / vola_table
    # sum inv.vola for all selected stocks.
    sum_inv_vola = np.sum(inv_vola_table)

    vola_target_weights = inv_vola_table / sum_inv_vola

    finish = time.perf_counter()

    print(f'Success! :) I finished building your list in {round(finish - start, 2)} second(s)')

    print("\n" + break_str + "\n")

    return final_buy_list, vola_target_weights

#print(build_mom_list())