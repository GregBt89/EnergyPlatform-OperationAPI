from beanie import Document
from fastapi import HTTPException
from bson import ObjectId

from ...internal import schemas
from ...db import models as m #models import MeterCatalog, PODCatalog, ECCatalog, ECMembersCatalog, AssetsCatalog
from typing import List
from .common import CommonServices

class CatalogServices(CommonServices):
    
    def _initialize_meter_catalog(self, to_insert: schemas.MeterAndPODs) -> m.MeterCatalog:
        return self._initialize_document(m.MeterCatalog, to_insert.model_dump(exclude={"pods"}))
    
    def _initialize_pod_catalog(self, to_insert: schemas.POD) -> m.PODCatalog:
        to_insert_dict = self._to_dictionary(to_insert)
        return self._initialize_document(m.PODCatalog, to_insert_dict)
    
    def _unpack_single_pod(self, pod:schemas.PODBase, meter_id:int)-> dict:
        pod_data = pod.model_dump()
        pod_data["meter_id"] = meter_id
        return schemas.POD(**pod_data)

    def _unpack_pods_of_meter(self, meter:schemas.MeterAndPODs) -> List[schemas.POD]:
        pods = list()
        meter_id = meter.meter_id
        for pod in meter.pods:
            pods.append(
                self._unpack_single_pod(
                    pod,
                    meter_id)
                )
        return pods

    async def _insert_new_meters(self, meters: List, pods: dict, session=None):
        pods["all"] = list()
        _meters = await m.MeterCatalog.insert_many(meters, session=session)
        meters_result = await m.MeterCatalog.by_ids(_meters.inserted_ids)
        for meter, _id in zip(meters, _meters.inserted_ids):
            for pod in pods[meter.meter_id]:
                pod.set_meter_mongo_id(_id)
                pods["all"].append(pod)
        pods_result = await self.add_pod_ids_in_catalogs(pods["all"], session=session)
        return meters_result, pods_result

    async def add_meter_and_pod_ids_in_catalogs(self, new_meters:schemas.MetersAndPODs):
        
        meters_to_insert = list()
        pods_to_insert = dict()

        for new_meter in new_meters.meters:
            pods_list = list()
            
            meters_to_insert.append(
                self._initialize_meter_catalog(new_meter)
                    )
            pods_list.extend(
                    self._unpack_pods_of_meter(new_meter)
                    )
            
            pods_to_insert[new_meter.meter_id] = pods_list

        meters, pods = await self.create_transaction(
            self._insert_new_meters, meters_to_insert, pods_to_insert)

        return meters, pods
    
    async def _insert_new_pods(self, pods, session):
        return await m.PODCatalog.insert_many(pods, session=session) 
    
    async def _handle_empty_meter_mongo_id(self, meter_id:int):
        meter = await self.check_if_meter_exists(meter_id)
        if not meter:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find meter {meter_id}"
                )
        return meter.id
    
    async def _handle_empty_members_mongo_id(self, meter_id:int):
        meter = self.check_if_meter_exists(meter_id)
        if not meter:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find meter {meter_id}"
                )
        return meter.id
    
    async def add_pod_ids_in_catalogs(self, new_pods: List[schemas.POD], session=None):
        pods = list()
        for new_pod in new_pods:
            if not new_pod.get_meter_mongo_id():
                meter_id_mongo = await self._handle_empty_meter_mongo_id(
                    new_pod.meter_id)
                new_pod.set_meter_mongo_id(meter_id_mongo)
            pods.append(
                self._initialize_pod_catalog(new_pod))
            
        inserted_pods = await self._insert_new_pods(pods, session)  
        return await m.PODCatalog.by_ids(inserted_pods.inserted_ids, session=session)
    
    async def get_all_pods(self) -> List[m.PODCatalog]:
        return await m.PODCatalog.all()
    
    async def get_pods_of_meter(self, meter_id:int) -> List[m.PODCatalog]:
        return await m.PODCatalog.by_meter_id(meter_id)
    
    async def get_meter(self, meter_id:int) -> List[m.MeterCatalog]:
        return await m.MeterCatalog.fetch_one_with_pods(meter_id)
    
    async def get_all_meters(self) -> List[m.MeterCatalog]:
        return await m.MeterCatalog.all()
    
    def _to_dictionary(self, to_insert: schemas.POD | schemas.AssetCatalog)-> dict:
        _meter_mongo_id = to_insert.get_meter_mongo_id()
        to_insert = to_insert.model_dump(exclude={"meter_id"})
        to_insert["meter_mongo_id"] = _meter_mongo_id
        return to_insert

    def _initilize_asset_catalog(self, to_insert: schemas.AssetCatalog)->m.AssetsCatalog:
        to_insert_dict = self._to_dictionary(to_insert)
        return self._initialize_document(m.AssetsCatalog, to_insert_dict)
    
    async def _insert_new_assets(self, assets:List[m.AssetsCatalog], session=None):
        return await m.AssetsCatalog.insert_many(assets)

    async def add_asset_ids_in_catalogs(self, new_assets: schemas.AssetCatalog):
        assets = list()
        for new_asset in new_assets:
            new_asset.set_meter_mongo_id(
                await self._handle_empty_meter_mongo_id(new_asset.meter_id))
            assets.append(
                self._initilize_asset_catalog(new_asset))
        inserted_assets = await self.create_transaction(self._insert_new_assets, assets)
        return await m.AssetsCatalog.by_ids(inserted_assets.inserted_ids)
    
    async def check_if_meter_exists(self, meter_id):
        return await m.MeterCatalog.by_meter_id(meter_id)
    
    def _initialize_ec_catalog(self, to_insert:schemas.EC):
        pod_members_id = [member.get_pod_mongo_id() for member in to_insert.members]
        to_insert = to_insert.model_dump(exclude={"members"})
        to_insert["members_mongo_id"] = pod_members_id
        return self._initialize_document(m.ECCatalog, to_insert)
    
    async def insert_ec_and_members(self, new_ec:schemas.EC, session=None):
        ec = self._initialize_ec_catalog(new_ec)
        ec_result = await m.ECCatalog.insert_many([ec], session=session)
        new_ec.set_ec_mongo_id(ec_result.inserted_ids[0])
        members = await self.add_ec_member_parameters_in_catalogs(new_ec, session)
        return await m.ECCatalog.by_ids(ec_result.inserted_ids, session), members
    
    async def add_ec_id_in_catalogs(self, new_ec: schemas.EC):
        # Initialize EC object but exclude members for now

        member_ids = [pod.pod_id for pod in new_ec.members]
        members, _ = await m.PODCatalog.by_many_pod_id(member_ids)

        if not members:
            raise HTTPException(
                status_code=400,
                detail="PODs not found"
                )
        
        if len(members) != len(new_ec.members):
            raise HTTPException(
                status_code=400,
                detail="some PODs were not found"
                )
        
        for ec_member in new_ec.members:
            ec_member.set_pod_mongo_id(members[ec_member.pod_id])

        return await self.create_transaction(self.insert_ec_and_members, new_ec)

    async def check_if_ec_exists(self, ec_id:int):
        return await m.ECCatalog.by_ec_id(ec_id)
    
    def _initialize_ec_member_catalog(self, member: schemas.Member, ec_mongo_id: ObjectId):
        pod_mongo_id = member.get_pod_mongo_id()
        to_insert = member.model_dump(exclude="_pod_mongo_id")
        to_insert["pod_mongo_id"]=pod_mongo_id
        to_insert["ec_mongo_id"]=ec_mongo_id
        return self._initialize_document(m.ECMembersCatalog, to_insert)

    async def add_ec_member_parameters_in_catalogs(self, ec: schemas.Members, session=None):
    
        # get ec mongo id 
        if not ec.get_ec_mongo_id():
            ec_mongo = await self.check_if_ec_exists(ec.ec_id)
            if not ec_mongo:
                raise HTTPException(
                    status_code=404,
                    detail="EC {ec_id} not found"
                    )
            ec.set_ec_mongo_id(ec_mongo.id)
        
        pods = list()
        for pod in ec.members:
            pods.append(
                self._initialize_ec_member_catalog(
                    pod, ec.get_ec_mongo_id()
                    )    
                )
            
        members = await m.ECMembersCatalog.insert_many(pods, session=session)
        return await m.ECMembersCatalog.by_ids(members.inserted_ids, session)








        




'''



            
        in members:
            if not



            
        
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


    


'''