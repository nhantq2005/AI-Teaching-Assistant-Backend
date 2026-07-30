# from app.models import Option
# from app.schemas.option import OptionRequest
#
#
# class OptionService:
#     def __init__(self, session):
#         self.session = session
#
#     async def create_option(self, option_create: OptionRequest) -> Option:
#         try:
#             option = Option(**option_create.dict())
#             self.session.add(option)
#             await self.session.commit()
#             await self.session.refresh(option)
#             return option
#         except Exception as e:
#             await self.session.rollback()
#             raise e
#
#     async def update_option(self, option_id: int, option_update: OptionUpdate) -> Option:
#         try:
#             option = await self.session.get(Option, option_id)
#             if not option:
#                 raise Exception(f"Không tìm thấy option với id: {option_id}")
#
#             update_data = option_update.model_dump(exclude_unset=True)
#             for key, value in update_data.items():
#                 setattr(option, key, value)
#
#             await self.session.commit()
#             await self.session.refresh(option)
#             return option
#         except Exception as e:
#             await self.session.rollback()
#             raise e
#
#     async def delete_option(self, option_id: int) -> Option:
#         try:
#             option = await self.session.get(Option, option_id)
#             if not option:
#                 raise Exception(f"Không tìm thấy option với id: {option_id}")
#             await self.session.delete(option)
#             await self.session.commit()
#             return option
#         except Exception as e:
#             await self.session.rollback()
#             raise e