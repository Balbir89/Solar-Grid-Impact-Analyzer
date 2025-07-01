# Solar Grid Impact Analyzer: Optimizing Renewable Energy

## Project Overview

This project analyzes simulated energy data to forecast demand peaks and explore strategies for optimizing renewable energy integration (solar) within an energy grid context. It demonstrates advanced data analysis, forecasting, and visualization skills.

## Key Features

* **Data Simulation:** Generated realistic time-series data for energy demand and solar generation.

* **Data Analysis (EDA):** Explored consumption and generation patterns, seasonality, and trends.

* **Feature Engineering:** Created advanced time-based and lagged features for prediction.

* **Time Series Forecasting:** Developed a Random Forest model to predict net energy load.

* **Impact Visualization:** Illustrated the "Duck Curve" effect of solar integration.

* **Interactive Dashboard:** Built a web-based dashboard for data and insights visualization.

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

## Results and Insights

The project provides simulated energy data, EDA visualizations, model performance metrics, prediction plots, feature importance insights, and an interactive dashboard showcasing key energy load profiles and the duck curve effect.

## Future Enhancements

* Explored more advanced forecasting models (e.g., ARIMA, LSTM).

* Integrated real-world external data (weather, holidays).

* Developed optimization algorithms for demand-side management.

* Implemented a full-stack deployment for broader access.

## License

This project is open-sourced under the MIT License
