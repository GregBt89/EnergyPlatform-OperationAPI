from fastapi import APIRouter, status, HTTPException
from ..internal.schemas import Meter, POD, EC

from typing import List

router = APIRouter(tags=["Ecommunities"], prefix="/ecomms")
"""
@router.post("/producer")
async def add_new_producer_member(new_producer: ProducerMember):

    pod = await PODCatalog.by_pod_id(new_producer.pod_id)
    if not pod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'POD {new_producer.pod_id} not found.')
    
    ec = await ECCatalog.by_ec_id(new_producer.pod_id)
    if not ec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'EC {new_producer.ec_id} not found.')

    member = ProdECMembers(
        parameters=new_producer.parameters,
        ec_id=ec.id,
        pod_id=pod.id,
        timestamp=new_producer.timestamp)
    
    await member.create()
    return member

@router.post("/consumer")
async def add_new_consumer_member(new_consumer: ProducerMember):

    pod = await PODCatalog.by_pod_id(new_consumer.pod_id)
    if not pod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'POD {new_consumer.pod_id} not found.')
    
    ec = await ECCatalog.by_ec_id(new_consumer.pod_id)
    if not ec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'EC {new_consumer.ec_id} not found.')

    member = ProdECMembers(
        parameters=new_consumer.parameters,
        ec_id=ec.id,
        pod_id=pod.id,
        timestamp=new_consumer.timestamp)
    await member.create()
    return member

@router.post("/pods")
async def add_new_pod(new_pods: List[POD]):
    pods = list()
    for new_pod in new_pods:
        meter_id_mongo = await MeterCatalog.by_meter_id(new_pod.meter_id)
        pods.append(
            PODCatalog(
                pod_id=new_pod.pod_id,
                pod_type=new_pod.pod_type,
                meter_id_mongo=meter_id_mongo.id
                )
            )
        await pods[-1].create()
    return pods

@router.post("/ec")
async def add_new_ec(new_ec: EC):
    members = await PODCatalog.by_many_pod_id(new_ec.members)
    ec = ECCatalog(
        ec_id=new_ec.ec_id,
        ec_type=new_ec.ec_type,
        members=members
        )
    await ec.create()
    return ec

"""
