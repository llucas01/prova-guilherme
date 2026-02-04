'''
  *** BaseDAO ***
  Classe abstrata base para DAOs (Data Access Objects)
  Operações CRUD genéricas
'''

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from supabase import Client

T = TypeVar('T')

class BaseDAO(ABC, Generic[T]):

  def __init__(self, client: Client, table_name: str):
    self._client = client
    self._table_name = table_name


  @abstractmethod
  def to_model(self, data: dict) -> T:
    pass

  @abstractmethod
  def to_dict(self, model: T) -> dict:
    pass

  def read(self, pk: str, value: T) -> Optional[T]:
    try:
      response = self._client.table(self._table_name).select('*').eq(pk, value).execute()
      if response.data and len(response.data) > 0:
        return self.to_model(response.data[0])
      return None
    except Exception as e:
      print(f'Erro ao buscar registro: {e}')
      return None

  def read_all(self) -> List[T]:
    try:
      response = self._client.table(self._table_name).select('*').execute()
      if response.data:
        return [self.to_model(item) for item in response.data]
      return []
    except Exception as e:
      print(f'Erro ao buscar todos os registros: {e}')
      return []
    
  def update(self, pk: str, value, model: T) -> Optional[T]:
    """
    Atualiza um registro existente.

    Args:
        pk (str): Nome da coluna chave primária (ex: 'cpf')
        value: Valor da chave primária do registro a atualizar
        model (T): Instância do modelo com os novos dados.

    Returns:
        Optional[T]: Instância atualizada ou None em caso de erro.
    """
    try:
        data = self.to_dict(model)
        
        data.pop(pk, None)
        data.pop('created_at', None)

        response = self._client.table(self._table_name).update(data).eq(pk, value).execute()

        if response.data and len(response.data) > 0:
            return self.to_model(response.data[0])
        return None
    except Exception as e:
        print(f"Erro ao atualizar registro: {e}")
        return None

  def delete(self, pk: str, value) -> bool:
      """
      Deleta um registro pela chave primária.

      Args:
          pk (str): Nome da coluna chave primária (ex: 'cpf')
          value: Valor da chave primária do registro a deletar.

      Returns:
          bool: True se deletado com sucesso, False caso contrário.
      """
      try:
          response = self._client.table(self._table_name).delete().eq(pk, value).execute()
          return True
      except Exception as e:
          print(f"Erro ao deletar registro: {e}")
          return False
