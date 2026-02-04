from supabase import Client
from dao.base_dao import BaseDAO
from models.funcionario import Departamento

class DepartamentoDAO(BaseDAO[Departamento]):

  def __init__(self, client: Client):
    super().__init__(client, 'departamento')

  def to_model(self, data: dict) -> Departamento:
    return Departamento.from_dict(data)

  def to_dict(self, model: Departamento) -> dict:
    return model.to_dict()