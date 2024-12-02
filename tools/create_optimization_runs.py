import sys
import asyncio
sys.path.append(
    r"C:\Users\tecnicoloyolatech\Documents\GitLab\INDIGENER\apis\operation-api")
from datetime import datetime 
from tools.ingest import IngestOptimizationRuns

URL: str = f"http://localhost:8030/optimization"

start_date = datetime(2023, 1, 1, 0, 0, 0)
end_date = datetime(2023, 12, 23, 0, 0, 0)

i = IngestOptimizationRuns(url=URL, starting_date=start_date, end_date=end_date, buffer_days=3)

if __name__ == "__main__":
    asyncio.run(i.data_ingection_loop())
    pass

