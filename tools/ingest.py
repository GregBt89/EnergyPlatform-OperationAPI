import sys
import enum
sys.path.append(
    r"C:\Users\tecnicoloyolatech\Documents\GitLab\INDIGENER\apis\operation-api")
import pandas as pd
import httpx
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from datetime import timedelta, datetime, date
from app.validation.schemas.shOptimization import (
    AssetOptimizationResults,
    OptimizationRun
)
from app.db.models.mOptimization import (
    AssetSchedule,
    Schedule
)



ARBITRAGE = ["imported_power", "exported_power", "p_from_vpp",
             "p_to_vpp", "soc", "degradation_cal", "degradation_cyc"]
MFRR = ["ch_p_u", "dis_p_u", "ch_p_d", "dis_p_d"]
FINANCIAL_METRICS = ["p_from_vpp", "p_to_vpp"]
BEHAVIOR_METRICS = ["soc", "degradation_cal", "degradation_cyc"]
METRICS = FINANCIAL_METRICS + BEHAVIOR_METRICS
RESULTS_TYPE = {**{x: "setpoints" for x in ARBITRAGE+MFRR}, **{
    x: "metrics" for x in METRICS}}
SERVICES = {**{x: "arbitrage" for x in ARBITRAGE}, **{x: "mfrr" for x in MFRR}}
UNITS = {**{x: "kW" for x in ARBITRAGE+MFRR +
         FINANCIAL_METRICS}, **{x: "kWh" for x in BEHAVIOR_METRICS}}
SERVICE_MAP = {"arbitrage": ARBITRAGE, "mfrr": MFRR}


def custom_encoder(data):
    if isinstance(data, enum.Enum):
        return data.value  # Convert Enum to its value
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, date):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: custom_encoder(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [custom_encoder(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


class BESS(BaseModel):
    timestamp: datetime = Field(
        ..., description="The timestamp of the values")
    asset_id: str = Field(
        ..., description="The id of the asset of AssetCatatlogs in MongoDb")
    ch_p_u: str = Field(
        ..., description="Charging power of the battery contributing to the upward mFRR product in period t (kW).")
    dis_p_u: str = Field(
        ..., description="Discharging power of the battery contributing to the upward mFRR product in period t (kW).")
    ch_p_d: str = Field(
        ..., description="Charging power of the battery contributing to the downward mFRR product in period t (kW).")
    dis_p_d: str = Field(
        ..., description="Discharging power of the battery contributing to the downward mFRR product in period t (kW).")
    p_from_vpp: str = Field(
        ..., description="Power transferred from the VPP to BESS in period t (kW).")
    p_to_vpp: str = Field(
        ..., description="Power transferred from the BESS to the VPP in period t (kW).")
    imported_power: str = Field(
        ..., description="Charging power of the BESS scheduled for the day-ahead market in period t (kW)")
    exported_power: str = Field(
        ..., description="Discharging power of the BESSscheduled for the day-ahead market in period t (kW).")
    degradation_cal: str = Field(
        ..., description="Estimated calendar degradation of the BESS due to operation in period t (kWh)")
    degradation_cyc: str = Field(
        ..., description="Estimated cycle degradation of the BESS due to operation in period t (kWh).")
    soc: str = Field(
        ..., description="State of charge of the BESS in period t (kWh).")


class Ingest:
    def __init__(self, url: str, starting_date: datetime, end_date: datetime, buffer_days: int):
        self.url = url
        # Rolling window logic
        self.window_size = timedelta(days=buffer_days)
        self.start = starting_date
        self.end = end_date

        self.current_end = None
        self.current_start = None

    def _set_current_end(self):
        self.current_end = self.current_start + self.window_size

    def update_rolling_window(self):

        if not self.current_start:
            self.current_start = self.start
        else:
            # Move the window forward by 1 day
            self.current_start += timedelta(days=1)
        self._set_current_end()

    def _intialize_model(model: BaseModel, data: List[Dict]):
        if not isinstance(data, list):
            data = [data]
        return [model(**datum) for datum in data]

    def get_initial_window_data(self, df: pd.DataFrame) -> List[Dict]:
        return self.get_next_window_data(df)

    def get_next_window_data(self, df: pd.DataFrame) -> List[Dict]:
        self.update_rolling_window()
        # Filter data within the rolling window
        start_index = (df["timestamp"] >= self.current_start)
        end_index = (df["timestamp"] < self.current_end)
        return df[start_index & end_index].to_dict(orient='series')
    
    async def make_requests(self, payload):
        # Send data to the API
        try:
            print(custom_encoder(payload))
            response = await self.client.post(self.url, json=custom_encoder(payload))
            response.raise_for_status()
            print(
                f"Data successfully sent for window: {self.current_start} to {self.current_end}")
        except httpx.RequestError as e:
            print(
                f"An error occurred while requesting {e.request.url}.")
        except httpx.HTTPStatusError as e:
            print(
                f"Error response {e.response.status_code} while sending data: {e.response.text}")
    
class IngestOptimizationRuns(Ingest):
    
    async def data_ingection_loop(self):
        self.update_rolling_window()
        async with httpx.AsyncClient() as self.client:
            while self.current_end <= self.end:
                payload = OptimizationRun(valid_from=self.current_start, valid_until=self.current_end)
                await self.make_requests(payload.model_dump(exclude_none=True))
                self.update_rolling_window()


class IngestBESSOptimizationResults(Ingest):

    def to_schedule(self, variable, columns: Dict[str, List]):
        return Schedule(**{
            "results_type": RESULTS_TYPE[variable],
            "variable": variable,
            "unit": UNITS[variable],
            "values": columns[variable]}
        )

    def to_asset_schedule(self, columns):
        schedules = list()
        ts = columns["timestamp"]
        del columns["timestamp"]

        for service, variables in SERVICE_MAP.items():
            schedules.append(
                AssetSchedule(
                    service=service,
                    schedule=[
                        self.to_schedule(
                            variable,
                            columns={
                                "timestamps": ts,
                                variable: columns[variable]
                            }
                        ) for variable in variables]))
        return schedules

    async def data_ingection_loop(self, data: pd.DataFrame, runIds):
        c = 0 
        run_id = runIds.loc[c]
        columns = self.get_initial_window_data(data)
        asset_id = columns["asset_id"].loc[0]
        async with httpx.AsyncClient() as client:
            while self.current_end <= self.end:
                del columns["asset_id"]
                payload = [
                    AssetOptimizationResults(
                        asset_id=asset_id,
                        timestamp=columns["timestamp"],
                        results=self.to_asset_schedule(columns)).model_dump(exclude_none=False)
                ]
                # Send data to the API
                try:

                    response = await client.post(self.url + run_id.values[0], json=custom_encoder(payload))
                    response.raise_for_status()
                    print(
                        f"Data successfully sent for window: {self.current_start} to {self.current_end}")
                except httpx.RequestError as e:
                    print(
                        f"An error occurred while requesting {e.request.url!r}.")
                except httpx.HTTPStatusError as e:
                    print(
                        f"Error response {e.response.status_code} while sending data: {e.response.text}")
                    # Move the window forward by 1 day

                columns = self.get_next_window_data(data)
                c += 1 
                try:
                    run_id = runIds.loc[c]
                except:
                    break

    async def inject_bess_optimization_results(self, data: List[BESS], runIds:pd.DataFrame,):
        await self.data_ingection_loop(data, runIds)
