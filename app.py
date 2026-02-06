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
    return render_template("index.html", titulo_do_meu_crud="CRUD LEGAL", app_name="TABELA LEGAL DO CRUD LEGAL", funcionarios=funcionario_dao.read_all())

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
    if request.method == "POST":
        try:
            # 1. Criar objeto novo
            funcionario_novo = Funcionario(
                 _cpf = request.form["cpf"],
                 _pnome = request.form["pnome"],
                 _unome = request.form["unome"],
                 _data_nasc = request.form["data_nasc"],
                _salario = request.form["salario"],
                _endereco = request.form["endereco"],
                _sexo = request.form["sexo"],
            )
                
            # 2. Cria um novo funcionario no banco
            resultado = funcionario_dao.create(funcionario_novo) #Aqui acontece a
                
            if resultado:
                return redirect(url_for('index'))
            else:
                return "Erro ao atualizar"
                
        except Exception as e:
            print(f"Erro: {e}")  # Para ver o erro no terminal
            return f"Ocorreu um erro: {e}"
    
    return render_template('create.html', datetime=datetime)

### Verifica se rota é GET ou POST para atualizar funcionário
@app.route('/funcionario/edit/<string:pk>', methods=['GET', 'POST'])
def update(pk):
    if request.method == 'POST':
        try:
            # 1. Pegar dados do formulário
            dados = request.form
            
            # 2. Buscar funcionário atual
            funcionario_atual = funcionario_dao.read('cpf', pk)
            if not funcionario_atual:
                return "Funcionário não encontrado"
            
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
            
            # 5. Atualizar no banco
            resultado = funcionario_dao.update('cpf', pk, funcionario_atualizado)
            
            if resultado:
                return redirect(url_for('index'))
            else:
                return "Erro ao atualizar"
                
        except Exception as e:
            return f"Erro: {str(e)}", 500
    
    # GET: Mostrar formulário
    funcionario = funcionario_dao.read('cpf', pk)
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)

### Verifica se rota é GET ou POST para remover funcionário
@app.route('/funcionario/delete/<string:pk>', methods=['GET', 'POST'])
def delete(pk):
    # Se for POST (ou seja, envio do formulário de confirmação)
    if request.method == 'POST':
        sucesso = funcionario_dao.delete('cpf', pk) # AQUI ACONTECE A MÁGICA - EXCLUI FUNCIONÁRIO
            
        if sucesso:
            return redirect(url_for('index'))

    funcionario = funcionario_dao.read('cpf', pk)
        
    return render_template('delete.html', funcionario=funcionario, datetime=datetime)