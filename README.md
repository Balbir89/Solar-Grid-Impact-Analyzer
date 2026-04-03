#  Solar Grid Intelligence: Strategic Peak-Shaving & ROI Optimization

### **Executive Summary**
This project addresses the "Duck Curve" challenge in the German energy market. By analyzing real-time solar yield against grid pricing, this model identifies a **15% reduction in operational energy costs** through automated "Sell vs. Store" arbitrage.

---

### The Problem
Industrial energy consumers in Germany face aggressive peak-hour tariffs (up to €0.42/kWh). Without an optimized discharge strategy, solar-integrated grids often "leak" value by selling power during low-demand windows and purchasing expensive grid power during sunset peaks.

---


###  Business Impact
* **Cost Avoidance:** Optimized battery discharge cycles to avoid peak-hour tariffs (€0.42/kWh vs €0.28/kWh).
* **Carbon Offset:** Quantified a reduction of **12.4 Tons of CO2** annually by prioritizing self-generation over grid dependency.
* **Investment ROI:** Provides a 24-month look-ahead to justify capital expenditure on BESS (Battery Energy Storage Systems).


---

###  Technical Architecture
* **Python (Pandas/NumPy):** Time-series alignment of weather data and price telemetry.
* **SQL (Window Functions):** Calculated rolling 7-day volatility and identified "High-Load" anomalies.
* **Predictive Modeling:** Linear & Polynomial regression to forecast solar yield with 92% accuracy.
* **Visualization:** 3D Surface Mapping of the "Profitability Frontier" (Price vs. Yield vs. Battery State).

---

###  Key Insights
1.  **The "5 PM Gap":** Identified that 40% of grid costs occur during the sunset window where solar drops but demand remains high.
2.  **Efficiency Loss:** Detected a 4% hardware degradation rate by comparing theoretical yield vs. actual sensor data.
3.  **Arbitrage Logic:** Developed a "Smart Trigger" that holds battery power until the grid price exceeds €0.38/kWh.

---

### **How to Run**
1. Clone the repo: `git clone https://github.com/Balbir89/Solar_Grid_Optimization.git`
2. Install dependencies: `pip install pandas numpy plotly scikit-learn`
3. Run the main analysis: `python solar_optimizer.py`


---

##  Dashboard  
### Example Output Visualization
![Dashboard](images/dashboard.png)

