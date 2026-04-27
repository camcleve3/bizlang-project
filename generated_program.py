import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sales.csv")
result = df.groupby("month", as_index=False)["revenue"].sum()
result.plot(kind="bar", x="month", y="revenue")
plt.tight_layout()
plt.show()

print(result)