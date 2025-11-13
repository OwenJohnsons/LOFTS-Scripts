#%%
import pandas as pd 
import matplotlib.pyplot as plt
import scienceplots 
plt.style.use(['science','ieee'])

tsys = pd.read_csv('Tsys.csv')

print(tsys.head())