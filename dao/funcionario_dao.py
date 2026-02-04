from typing import Optional
from supabase import Client
from dao.base_dao import BaseDAO
from models.funcionario import Funcionario

class FuncionarioDAO(BaseDAO[Funcionario]):

  def __init__(self, client: Client):
    super().__init__(client, 'funcionario')

  def to_model(self, data: dict) -> Funcionario:
    return Funcionario.from_dict(data)

  def to_dict(self, model: Funcionario) -> dict:
    return model.to_dict()

  # Métodos específicos para Funcionario (usando CPF como chave primária)
  def read_by_cpf(self, cpf: str) -> Optional[Funcionario]:
    """Busca um funcionário pelo CPF"""
    return self.read('cpf', cpf)

  def update_by_cpf(self, cpf: str, funcionario: Funcionario) -> Optional[Funcionario]:
    """Atualiza um funcionário pelo CPF"""
    return self.update('cpf', cpf, funcionario)

  def delete_by_cpf(self, cpf: str) -> bool:
    """Deleta um funcionário pelo CPF"""
    return self.delete('cpf', cpf)