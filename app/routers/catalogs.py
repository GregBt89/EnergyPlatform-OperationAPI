from fastapi import APIRouter, status, HTTPException
from ..internal import schemas
from ..db.models import MeterCatalog, PODCatalog, ECCatalog, ECMembersCatalog, AssetsCatalog
from typing import List

router = APIRouter(tags=["Catalogs"], prefix="/catalogs")

@router.post("/meters")
async def add_new_meter(new_meters: schemas.MetersAndPODs):
    meters_to_insert = list()
    pods_to_insert = list()
    for new_meter in new_meters.meters:
        meters_to_insert.append(
            MeterCatalog(
                meter_id=new_meter.meter_id,
                meter_type=new_meter.meter_type
                )
            )
        for pod in new_meter.pods:
            pods_to_insert.append(
                schemas.POD(pod_id=pod.pod_id,
                            pod_type=pod.pod_type,
                            meter_id= new_meter.meter_id))
            
    meters = await MeterCatalog.insert_many(meters_to_insert)

    pods = await add_new_pod(pods_to_insert)

    return await MeterCatalog.by_ids(meters.inserted_ids), pods

@router.post("/pods")
async def add_new_pod(new_pods: List[schemas.POD]):
    pods = list()
    for new_pod in new_pods:
        meter_id_mongo = await MeterCatalog.by_meter_id(new_pod.meter_id)
        if not meter_id_mongo:
            raise HTTPException(status_code=400,
                                detail=f"Could not find meter {new_pod.meter_id} for pod {new_pod.pod_id} in operation db.")
        pods.append(
            PODCatalog(
                pod_id=new_pod.pod_id,
                pod_type=new_pod.pod_type,
                meter_mongo_id=meter_id_mongo.id
                )
            )
    inserted_pods = await PODCatalog.insert_many(pods)  
    return await PODCatalog.by_ids(inserted_pods.inserted_ids)

@router.get("/pods")
async def get_pods():
    return await PODCatalog.by_many_pod_id([1, 2])

@router.post("/ec")
async def add_new_ec(new_ec: schemas.EC):
    member_ids = [pod.pod_id for pod in new_ec.members]
    members_mongo_ids = await PODCatalog.by_many_pod_id(member_ids)

    if not members_mongo_ids:
        raise HTTPException(
            status_code=400,
            detail="PODs not found"
            )
    if len(members_mongo_ids) != len(new_ec.members):
        raise HTTPException(
            status_code=400,
            detail="some PODs were not found"
            )

    ec = ECCatalog(
        ec_id=new_ec.ec_id,
        ec_model_id=new_ec.ec_model_id,
        members=members_mongo_ids
        )
    
    await ec.create()
    members = await add_new_ec_members(new_ec)
    return ec, members

@router.post("/ec/members")
async def add_new_ec_members(ec: schemas.Members):
    ec_mongo = await ECCatalog.by_ec_id(ec.ec_id)
    if not ec_mongo:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find ec {ec.ec_id}."
            )
    
    to_insert = []
    for member in ec.members:
        pod_mongo = await PODCatalog.by_pod_id(member.pod_id)
        if not pod_mongo:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find POD {member.pod_id}."
            )
        
        to_insert.append(
            ECMembersCatalog(
                ec_mongo_id=ec_mongo.id,
                pod_mongo_id=pod_mongo.id,
                member_type=member.member_type.value, 
                timestamp=member.timestamp, 
                parameters=member.parameters.model_dump())
                )

    inserted_members = await ECMembersCatalog.insert_many(to_insert)  
    return await ECMembersCatalog.by_ids(inserted_members.inserted_ids)

@router.post("/assets")
async def add_new_asset(asset: schemas.AssetCatalog):
    meter_id_mongo = await MeterCatalog.by_meter_id(asset.meter_id)
    if not meter_id_mongo:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find meter {asset.meter_id}"
            )
    
    new_asset = AssetsCatalog(
        asset_id=asset.asset_id,
                              meter_id_mongo=meter_id_mongo,
                              asset_type=asset.asset_type)
    
    inserted_asset = await AssetsCatalog.insert_many([new_asset])
    return await AssetsCatalog.by_ids(inserted_asset.inserted_ids)
    

    





