# Original reference data

The earlier project generated 17,544 hourly observations for 2023–2024. This CSV is retained for provenance only. Its original generator had no fixed random seed. The rebuilt pipeline uses a new, seeded commercial-site scenario in kW/kWh, documented in config/default.json. It does not mix the original MW-scale data with the new scenario. Historical notebooks and the escaped dashboard have been replaced by the tested package; the previous files remain in Git history.
