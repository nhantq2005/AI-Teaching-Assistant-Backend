# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
# from app.db.session import get_db
# from app.schemas.option import OptionRequest, OptionResponse
# from app.services.option_service import OptionService
#
# router = APIRouter(prefix="/options", tags=["Options"])
#
# def get_option_service(db: AsyncSession = Depends(get_db)):
#     return OptionService(session=db)
#
# @router.post("/", response_model=OptionResponse)
# async def create_option(option: OptionRequest, service: OptionService = Depends(get_option_service)):
#     return await service.create_option(option_create=option)
#
# @router.put("/{option_id}", response_model=OptionResponse)
# async def update_option(option_id: int, option: OptionUpdate, service: OptionService = Depends(get_option_service)):
#     try:
#         db_option = await service.update_option(option_id=option_id, option_update=option)
#         return db_option
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
#
# @router.delete("/{option_id}")
# async def delete_option(option_id: int, service: OptionService = Depends(get_option_service)):
#     try:
#         await service.delete_option(option_id=option_id)
#         return {"message": "Option deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
