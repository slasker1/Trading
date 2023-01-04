from twap_obj import Initialize

break_str = '#' * 100

if __name__ == '__main__':
    print(break_str)
    print('Welcome Trader! To begin your analysis please follow the input instructions:\n')
    ticker = input('Please enter a ticker to anlayze: ')
    time = input('Please enter the amount of trading days: ')

    selection = Initialize(ticker, time)

    print('\n' + break_str + '\nDisplaying your selection: ')
    Initialize.displaySelection(selection)

    TWAP = selection.returnTWAP

    print(TWAP)

    print('The TWAP of ' + ticker + ' for ' + time + ' trading days = ' + str(TWAP))