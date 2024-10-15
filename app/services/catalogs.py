from fastapi import HTTPException
from ..db.models import catalogs as m
from bson import ObjectId
from typing import List
from .common import CommonServices
from ..schemas.catalogs import (
    POD,
    MeterAndPODs,
    Meter,
    AssetCatalog,
    EC,
    Member
)

Assets = List[AssetCatalog]


class CatalogServices(CommonServices):

    def _initialize_meter_catalog(self, to_insert: MeterAndPODs) -> m.MeterCatalog:
        return self._initialize_document(m.MeterCatalog, to_insert.model_dump())

    async def _initialize_pod_catalog(self, pod: POD) -> m.PODCatalog:
        if not pod.get_meter_mongo_id():
            meter_id_mongo = await self._get_meter_mongo_id(pod.meter_id)
            pod.set_meter_mongo_id(meter_id_mongo)
        return self._initialize_document(m.PODCatalog, self._to_dictionary(pod))

    async def _initilize_asset_catalog(self, asset: AssetCatalog) -> m.AssetsCatalog:
        if not asset.get_meter_mongo_id():
            meter_id_mongo = await self._get_meter_mongo_id(asset.meter_id)
            asset.set_meter_mongo_id(meter_id_mongo)
        return self._initialize_document(m.AssetsCatalog, self._to_dictionary(asset))

    async def add_meters(self, new_meters: List[Meter]) -> None:

        meters = list()

        for new_meter in new_meters:
            meters.append(
                self._initialize_meter_catalog(new_meter)
            )

        await self.create_transaction(
            m.MeterCatalog.insert_many, meters)

    async def _get_meter_mongo_id(self, meter_id: int):
        meter = await self.check_if_meter_exists(meter_id)
        if not meter:
            raise ValueError(f"Could not find meter {meter_id}")
        return meter.id

    async def add_pods(self, new_pods: List[POD]):
        pods = list()
        for new_pod in new_pods:
            await pods.append(
                self._initialize_pod_catalog(new_pod))
        await self.create_transaction(m.PODCatalog.insert_many, pods)

    async def get_all_pods(self) -> List[m.PODCatalog]:
        return await m.PODCatalog.all()

    async def get_pods_of_meter(self, meter_id: int) -> List[m.PODCatalog]:
        return await m.PODCatalog.by_meter_id(meter_id)

    async def get_meter(self, meter_id: int) -> List[m.MeterCatalog]:
        return await m.MeterCatalog.fetch_one_with_pods(meter_id)

    async def get_all_meters(self) -> List[m.MeterCatalog]:
        return await m.MeterCatalog.all()

    def _to_dictionary(self, to_insert: POD | AssetCatalog) -> dict:
        _meter_mongo_id = to_insert.get_meter_mongo_id()
        to_insert = to_insert.model_dump(exclude={"meter_id"})
        to_insert["meter_mongo_id"] = _meter_mongo_id
        return to_insert

    async def add_asset_ids_in_catalogs(self, new_assets: Assets) -> None:
        print(self.client.session)
        assets = list()
        for new_asset in new_assets:
            assets.append(
                await self._initilize_asset_catalog(new_asset))
        await self.create_transaction(m.AssetsCatalog.insert_many, assets)

    async def check_if_meter_exists(self, meter_id):
        return await m.MeterCatalog.by_meter_id(meter_id)

    ''' 
    def _initialize_ec_catalog(self, to_insert: EC):
        pod_members_id = [member.get_pod_mongo_id()
                          for member in to_insert.members]
        to_insert = to_insert.model_dump(exclude={"members"})
        to_insert["members_mongo_id"] = pod_members_id
        return self._initialize_document(m.ECMembersCatalog, to_insert)

    async def add_ec_id_in_catalogs(self, new_ec: List[EC]):
        # Initialize EC object but exclude members for now

        member_ids = [pod.pod_id for pod in new_ec]
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

        for ec_member in new_ec:
            ec_member.set_pod_mongo_id(members[ec_member.pod_id])
        
        return await self.create_transaction(self.insert_ec_and_members, new_ec)
        
        async def check_if_ec_exists(self, ec_id: int):
        return await m.ECCatalog.by_ec_id(ec_id)
        
        '''

    def _initialize_ec_member_document(self, member: Member, pod_mongo_id: ObjectId):
        member.set_pod_mongo_id(pod_mongo_id)
        return m.ECMembersCatalog(
            pod_mongo_id=pod_mongo_id,
            **member.model_dump(exclude={"pod_id"})
        )

    async def add_ec_member_parameters_in_catalogs(self, members: List[EC]):

        member_ids = [pod.pod_id for pod in members]
        pods, _ = await m.PODCatalog.by_many_pod_id(member_ids)

        if (not pods) or (len(pods) != len(members)):
            raise ValueError("Not all Pods found")

        for i, member in enumerate(members):
            members[i] = self._initialize_ec_member_document(
                member, pods[member.pod_id]
            )
        await self.create_transaction(m.ECMembersCatalog.insert_many, members)
