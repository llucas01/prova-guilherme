from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from config.database import SupabaseConnection
#importando de arquivos .py
from dao.funcionario_dao import FuncionarioDAO
from models.funcionario import Funcionario

app = Flask(__name__)


#se conectando ao supabase
client = SupabaseConnection().client

#Caminho do index
@app.route("/")
def index():
    return render_template("index.html", title="CRUD LEGAL", app_name="TABELA DE USER", funcionarios=funcionario_dao.read_all())

# Criando DAO para acessar a tabela funcionario
funcionario_dao = FuncionarioDAO(client)

# Filtro personalizado para formatar CPF
@app.template_filter('format_cpf')
def format_cpf(cpf):
    """Formata CPF no padrão XXX.XXX.XXX-XX"""
    if not cpf or len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

@app.route("/funcionario/<string:pk>/<int:id>")
def details(pk, id):
    funcionario = funcionario_dao.read(pk, id)
    return render_template("details.html", funcionario=funcionario, datetime=datetime)

# Rota para CRIAR novo funcionário
@app.route('/funcionario/novo', methods=['GET', 'POST'])
def create():
    return render_template('create.html')

### Verifica se rota é GET ou POST para atualizar funcionário
@app.route('/funcionario/edit/<string:pk>', methods=['GET', 'POST'])
def update(pk):
    print(f"\n🔧 UPDATE chamado - CPF: {pk}, Método: {request.method}")
    
    if request.method == 'POST':
        try:
            # 1. Pegar dados do formulário
            dados = request.form
            print(f"Dados recebidos: {dict(dados)}")
            
            # 2. Buscar funcionário atual
            funcionario_atual = funcionario_dao.read('cpf', pk)
            if not funcionario_atual:
                return "Funcionário não encontrado", 404
            
            # 3. Converter tipos
            from datetime import datetime as dt
            
            # Data de nascimento
            data_nasc = funcionario_atual.data_nasc
            if dados.get('data_nasc'):
                try:
                    data_nasc = dt.strptime(dados['data_nasc'], '%Y-%m-%d').date()
                except:
                    pass  # Mantém a atual se der erro
            
            # Salário
            salario = funcionario_atual.salario
            try:
                salario = float(dados.get('salario', salario))
            except:
                pass
            
            # Número departamento
            num_depto = dados.get('numero_departamento')
            numero_departamento = None
            if num_depto and num_depto.strip():
                try:
                    numero_departamento = int(num_depto)
                except:
                    numero_departamento = funcionario_atual.numero_departamento
            
            # CPF supervisor
            cpf_supervisor = dados.get('cpf_supervisor')
            if cpf_supervisor and cpf_supervisor.strip():
                cpf_supervisor = cpf_supervisor.replace('.', '').replace('-', '')
                if len(cpf_supervisor) != 11:
                    cpf_supervisor = None
            else:
                cpf_supervisor = None
            
            # 4. Criar objeto atualizado
            funcionario_atualizado = Funcionario(
                _cpf=pk,
                _pnome=dados.get('pnome', funcionario_atual.pnome),
                _unome=dados.get('unome', funcionario_atual.unome),
                _data_nasc=data_nasc,
                _endereco=dados.get('endereco', funcionario_atual.endereco),
                _salario=salario,
                _sexo=dados.get('sexo', funcionario_atual.sexo),
                _cpf_supervisor=cpf_supervisor,
                _numero_departamento=numero_departamento,
                _created_at=funcionario_atual.created_at
            )
            
            print(f"Criado objeto: {funcionario_atualizado}")
            
            resultado = funcionario_dao.update('cpf', pk, funcionario_atualizado)
            
            if resultado:
                return redirect(url_for('index'))
            else:
                return "Erro ao atualizar", 500
                
        except Exception as e:
            # Mostra erro simples sem traceback
            import traceback
            print(traceback.format_exc())  # Esta linha causa erro se não importar
            return f"Erro: {str(e)}", 500
    
    # GET: Mostrar formulário
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)
    
    # SE FOR GET: Mostrar formulário com dados atuais
    print(f"   📄 Mostrando formulário de edição")
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)

### Verifica se rota é GET ou POST para remover funcionário
@app.route('/funcionario/delete/<string:pk>', methods=['GET', 'POST'])
def delete(pk):
    # Se for POST (ou seja, envio do formulário de confirmação)
    if request.method == 'POST':
        try:
            # 1. Tenta excluir do banco de dados
            sucesso = funcionario_dao.delete('cpf', pk) # AQUI ACONTECE A MÁGICA - EXCLUI FUNCIONÁRIO
            
            if sucesso:
                return redirect(url_for('index'))
            else:
                return "Erro ao excluir funcionário", 500
                
        except Exception as e:
            return f"Erro: {str(e)}", 500
    
    # Se for GET, apenas exibe o funcionário a ser removido
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
        
    return render_template('delete.html', funcionario=funcionario, datetime=datetime)