import pandas as pd
import asyncio
from ingest import IngestBESSOptimizationResults
OPTIMIZATION_RUN_IDs: str = f"aws\debug\data\optimization_ids.csv"
URL: str = "http://localhost:8030/optimization/"
RESULTS_FILEPATH = f"aws\debug\data\LIB.csv"


df = pd.read_csv(RESULTS_FILEPATH, header=0)
df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d/%m/%y %H:%M")

runIds = pd.read_csv(OPTIMIZATION_RUN_IDs, header=0)

start_date = df["timestamp"].loc[0]
end_date = df["timestamp"].loc[1000]

print(f"Start Date: {start_date}")
print(f"  End Date: {end_date}\n")


async def ingest():
    store_results = IngestBESSOptimizationResults(
        URL, starting_date=start_date, end_date=end_date, buffer_days=3)

    await store_results.inject_bess_optimization_results(df, runIds)

if __name__ == "__main__":
    asyncio.run(ingest())
    pass
