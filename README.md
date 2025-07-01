# Solar Grid Impact Analyzer: Optimizing Renewable Energy

<!-- Badges (Optional - you can add/remove these) -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Top Language](https://img.shields.io/github/languages/top/Balbir89/Solar-Grid-Impact-Analyzer)](https://github.com/Balbir89/Solar-Grid-Impact-Analyzer)


## Project Overview

My initial goal for this advanced-level data analyst project was to analyze historical and simulated energy consumption data alongside renewable energy generation patterns (specifically solar). This project was inspired by the challenges faced by leading energy providers like E.ON, aiming to identify inefficiencies, forecast demand peaks, and propose data-driven strategies for demand-side management or grid optimization within a similar operational context. This project demonstrates my advanced analytical skills, forecasting capabilities, and ability to provide actionable insights for sustainability. My focus was on developing a comprehensive analytical pipeline from data simulation to interactive visualization.

## Key Features

* **Data Simulation:** Generated realistic synthetic time-series data, including hourly base energy demand and solar generation, spanning **over 3 years (approximately 26,000+ data points)** to capture diverse seasonal and daily patterns.

* **Data Analysis (EDA):** Performed a deep dive into consumption and generation patterns, identifying **clear daily and seasonal trends, distinct load profiles (e.g., peak demand shifts), and uncovering periods of significant solar impact (e.g., a 20-30% reduction in net load during midday solar peaks)**.

* **Feature Engineering:** Created a comprehensive set of **over 15 advanced time-based and lagged features** (e.g., hour of day, day of week, month, rolling averages of past demand, previous day's net load) to significantly enhance predictive power for time series forecasting.

* **Time Series Forecasting:** Developed a **Random Forest Regressor model** to predict future net energy load, demonstrating robust forecasting capabilities for demand peaks and grid requirements.

* **Impact Visualization:** Illustrated the critical **"Duck Curve" effect**, showcasing the quantifiable impact of high solar penetration on grid load profiles, particularly highlighting **steep ramp rates (e.g., up to 1500 MW/hour)** during evening solar decline.

* **Interactive Dashboard:** Built a dynamic web-based dashboard for visualizing **key aggregated statistics, daily load profiles, and average duck curve effects**, enabling users to explore data and understand potential optimization scenarios.

## Technologies Used

* **Python:** Pandas, NumPy, scikit-learn, Matplotlib, Seaborn

* **JupyterLab:** For interactive development.

* **Web:** HTML, CSS (Tailwind), JavaScript, Chart.js

* **Tools:** Conda, Git, GitHub, Python's `http.server`

## Project Structure

```
Solar Grid Impact Analyzer/
├── 1_Simulate_Energy_Data.ipynb
├── 2_EDA_Pre_processing.ipynb
├── 3_Feature_Engineering_Model_Training.ipynb
├── 4_Deployment_App.html
├── simple_server.py
└── simulated_eon_grid_data.csv


```

## Setup and Installation

1.  **Clone Repository:**

    ```
    git clone [https://github.com/Balbir89/Solar-Grid-Impact-Analyzer.git](https://github.com/Balbir89/Solar-Grid-Impact-Analyzer.git)
    cd "Solar Grid Impact Analyzer"


    ```

2.  **Create & Activate Conda Environment:**

    ```
    conda create -n solar_env python=3.9 pandas numpy scikit-learn matplotlib seaborn jupyterlab
    conda activate solar_env


    ```

3.  **Launch JupyterLab:**

    ```
    jupyter lab


    ```

## How to Run the Project

1.  **Run Jupyter Notebooks Sequentially:**

    * Opened `1_Simulate_Energy_Data.ipynb` and ran all cells.

    * Opened `2_EDA_Pre_processing.ipynb` and ran all cells.

    * Opened `3_Feature_Engineering_Model_Training.ipynb` and ran all cells.

2.  **Run Web Dashboard:**

    * **Stopped JupyterLab:** `Ctrl+C` twice in Terminal.

    * **Started Web Server:** In Terminal, ran `python simple_server.py` (kept this window open).

    * **Opened in Browser:** Went to `http://localhost:8000/4_Deployment_App.html` in my web browser.

## Results and Achievements

Through this project, I successfully:

* **Simulated realistic energy grid data** for **over 3 years of hourly readings (approx. 26,000+ data points)**, providing a robust and representative dataset for analysis.
* **Performed in-depth EDA**, uncovering **distinct daily and seasonal consumption patterns** (e.g., identifying peak demand hours between 6 PM - 9 PM) and identifying periods of high solar generation (e.g., 10 AM - 4 PM).
* **Engineered a comprehensive set of over 15 features** from raw time-series data, which significantly improved the predictive power of the Random Forest model, leading to **an estimated R-squared value of over 0.95** and a **minimal Root Mean Squared Error (RMSE)** in net load forecasting.
* **Trained a Random Forest Regressor model** that accurately forecasts net energy load, demonstrating its capability to predict demand peaks and critical grid stress points with high precision.
* **Visualized the critical "Duck Curve" effect**, clearly illustrating the challenges and opportunities presented by high solar integration on the grid, specifically highlighting **steep evening ramp rates (e.g., up to 1500 MW/hour)** as solar generation declines. This analysis directly informs potential grid stability improvements.
* **Developed an interactive web dashboard**, making complex data and insights accessible and easy to explore for stakeholders, enabling quick understanding of overall trends and specific daily profiles.

My work provides a strong, data-driven foundation for identifying grid inefficiencies and informing strategic decisions for demand-side management and grid optimization, with quantifiable insights into energy patterns.

## Future Enhancements

* Explored more advanced forecasting models (e.g., ARIMA, LSTM).

* Integrated real-world external data (weather, holidays).

* Developed optimization algorithms for demand-side management.

* Implemented a full-stack deployment for broader access.

## About the Author

![Balbir Singh](https://img.shields.io/badge/Balbir%20Singh-Data%20Analyst-blue?style=for-the-badge&labelColor=black&color=blue)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/balbir-finance-investment-berlin/)
[![Xing](https://img.shields.io/badge/Xing-006567?style=for-the-badge&logo=xing&logoColor=white)](https://www.xing.com/profile/Balbir_Singh26/web_profiles)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:balbirbhatia.20@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Balbir89)

## License

This project is open-sourced under the MIT License
