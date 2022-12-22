import tracker_functions as tf

print(f'''
**********************************************************************
{'Webscraping Track Drugstores - Options': ^70}
{'Type the letters after the option': ^70}

{'Collect data from DROGA RAIA: DRA': <70}
{'Collect data from DROGASIL: DSL': <70}
{'Collect data from DROGARIA SÃO PAULO: DSP': <70}
{'Collect data from DROGARIA PACHECO: DPA': <70}
{'Collect data from DROGARIA VENANCIO: DVN': <70}
{'Collect data from ÉPOCA COSMÉTICOS: ECM': <70}
{'Collect data from a custom group of drugstores: [Write the letters]': <70}
{'Collect data from all drugstores: ALL': <70}

{'Type Q to quit': ^70}
{'OBS: For the custom group write the letters in a list form': ^70}
{'EX: DRA, DSL, DVN': ^70}
**********************************************************************
''')

option = input('Type one of the options from above: ')

option = option.upper()

if option == 'ALL':

    drugstores = ['DRA', 'DSL', 'DSP', 'DPA', 'DVN', 'ECM']
    tf.track_price(drugstores)

elif option in 'DRA, DSL, DSP, DPA, DVN, ECM':

    drugstores = option.replace(' ','').split(',')
    tf.track_price(drugstores)

elif option == 'Q':
    print('Closing the program.')
    quit()

else:
    print('You have choosen an invalid option!')
    print('Please, review your letters and try again.')



