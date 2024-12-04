from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, List, Union
from beanie import PydanticObjectId
from bson import ObjectId


class BessMeasurementsIn(BaseModel):
    asset_id: str = Field(...,
                          description="The unique identifier for the asset")
    timestamp: datetime = Field(..., description="Time of the measurement")

    # Lithium battery measurements
    ch_p_u: Optional[float] = Field(
        None, description="Charging power for upward mFRR (kW)")
    dis_p_u: Optional[float] = Field(
        None, description="Discharging power for upward mFRR (kW)")
    ch_p_d: Optional[float] = Field(
        None, description="Charging power for downward mFRR (kW)")
    dis_p_d: Optional[float] = Field(
        None, description="Discharging power for downward mFRR (kW)")
    p_from_vpp: Optional[float] = Field(
        None, description="Power from VPP to battery (kW)")
    p_to_vpp: Optional[float] = Field(
        None, description="Power from battery to VPP (kW)")
    imported_power: float = Field(
        ..., description="Charging power scheduled for the day-ahead market (kW).")
    exported_power: float = Field(
        ..., description="Discharging power scheduled for the day-ahead market (kW).")
    # Degradation data for lithium battery
    degradation_cal: Optional[float] = Field(
        None, description="Calendar degradation of battery (kWh)")
    degradation_cyc: Optional[float] = Field(
        None, description="Cycle degradation of battery (kWh)")
    soc: float = Field(...,
                       description="State of charge of the battery (kWh)")

    class Config:
        from_attributes = True

    def model_dump(self, **kwargs) -> dict[str, Any]:
        result = super().model_dump(**kwargs)
        if not isinstance(result["asset_id"], ObjectId):
            result["asset_id"] = PydanticObjectId(result["asset_id"])
        return result


class AssetMeasurementsIn(BaseModel):
    asset_id: str = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    exported_power: float = Field(
        ..., description="Power from asset to Grid (kW)")

    class Config:
        from_attributes = True

    def model_dump(self, **kwargs) -> dict[str, Any]:
        result = super().model_dump(**kwargs)
        if not isinstance(result["asset_id"], ObjectId):
            result["asset_id"] = PydanticObjectId(result["asset_id"])
        return result


class MeasurementsOut(BaseModel):
    asset_id: str = Field(...,
                          description="The unique mongodb identifier for the asset")
    timestamps: List[datetime] = Field(...,
                                       description="Time of the measurement")

    # Lithium battery measurements
    ch_p_u: Union[None, List[Union[None, float]]] = Field(
        None, description="Charging power for upward mFRR (kW)")
    dis_p_u: Union[None, List[Union[None, float]]] = Field(
        None, description="Discharging power for upward mFRR (kW)")
    ch_p_d: Union[None, List[Union[None, float]]] = Field(
        None, description="Charging power for downward mFRR (kW)")
    dis_p_d: Union[None, List[Union[None, float]]] = Field(
        None, description="Discharging power for downward mFRR (kW)")
    p_from_vpp: Union[None, List[Union[None, float]]] = Field(
        None, description="Power from VPP to battery (kW)")
    p_to_vpp: Union[None, List[Union[None, float]]] = Field(
        None, description="Power from battery to VPP (kW)")
    imported_power: Optional[List[float]] = Field(
        None, description="Charging power scheduled for the day-ahead market (kW).")
    exported_power: List[float] = Field(
        ..., description="Injected power or Discharging power (kW).")

    # Degradation data for lithium battery
    degradation_cal: Optional[List[float]] = Field(
        None, description="Calendar degradation of battery (kWh)")
    degradation_cyc: Optional[List[float]] = Field(
        None, description="Cycle degradation of battery (kWh)")
    soc: Optional[List[float]] = Field(
        None, description="State of charge of the battery (kWh)")

    class Config:
        from_attributes = True


class PODMeasurementsIn(BaseModel):
    pod_id: str = Field(
        ..., description="he unique identifier for the POD")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    surplus: float = Field(
        ..., description="Surplus energy to grid (kWh)")
    consumption: float = Field(
        ..., description="Energy consummed from Grid (kWh)")

    class Config:
        from_attributes = True

    def model_dump(self, **kwargs) -> dict[str, Any]:
        result = super().model_dump(**kwargs)
        if not isinstance(result["pod_id"], ObjectId):
            result["pod_id"] = PydanticObjectId(result["pod_id"])
        return result


class PODMeasurementsOut(BaseModel):
    pod_id: str = Field(...,
                        description="The unique mongodb identifier for the asset")
    timestamps: List[datetime] = Field(...,
                                       description="Time of the measurement")
    surplus: List[float] = Field(
        ..., description="Surplus energy to grid (kWh)")
    consumption: List[float] = Field(
        ..., description="Energy consummed from Grid (kWh)")
