# Módulo de conexão com o Supabase
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

class SupabaseConnection:
  '''
  Padrão de Projeto - Singleton
  * Garante apenas uma instância em toda a aplicação
  '''
  _instance = None
  # Type Hint
  # * Garante o tipo de dado a ser atribuído a um atributo/variável
  _client: Client = None

  # new - cria a instância da classe
  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(SupabaseConnection, cls).__new__(cls)
      cls._instance._init_connection()
    return cls._instance
  
  def _init_connection(self):
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
      raise ValueError('Erro nas variáveis de ambiente ❌')

    self._client = create_client(supabase_url, supabase_key)
    print('Conexão com Supabase ✅')

  @property
  def client(self) -> Client: # Type Hint
    return self._client