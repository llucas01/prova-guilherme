from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from config.database import SupabaseConnection
from dao.funcionario_dao import FuncionarioDAO
from models.funcionario import Funcionario

app = Flask(__name__)


client = SupabaseConnection().client

@app.route("/")
def index():
    return render_template("index.html", title="CRUD LEGAL", app_name="TABELA DE USER", funcionarios=funcionario_dao.read_all())

funcionario_dao = FuncionarioDAO(client)

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

@app.route('/funcionario/novo', methods=['GET', 'POST'])
def create():
    return render_template('create.html')

@app.route('/funcionario/edit/<string:pk>', methods=['GET', 'POST'])
def update(pk):
    print(f"\n🔧 UPDATE chamado - CPF: {pk}, Método: {request.method}")
    
    if request.method == 'POST':
        try:
            dados = request.form
            print(f"Dados recebidos: {dict(dados)}")
            
            funcionario_atual = funcionario_dao.read('cpf', pk)
            if not funcionario_atual:
                return "Funcionário não encontrado", 404
            
            from datetime import datetime as dt
            
            data_nasc = funcionario_atual.data_nasc
            if dados.get('data_nasc'):
                try:
                    data_nasc = dt.strptime(dados['data_nasc'], '%Y-%m-%d').date()
                except:
                    pass  
            
            salario = funcionario_atual.salario
            try:
                salario = float(dados.get('salario', salario))
            except:
                pass
            
            num_depto = dados.get('numero_departamento')
            numero_departamento = None
            if num_depto and num_depto.strip():
                try:
                    numero_departamento = int(num_depto)
                except:
                    numero_departamento = funcionario_atual.numero_departamento
            
            cpf_supervisor = dados.get('cpf_supervisor')
            if cpf_supervisor and cpf_supervisor.strip():
                cpf_supervisor = cpf_supervisor.replace('.', '').replace('-', '')
                if len(cpf_supervisor) != 11:
                    cpf_supervisor = None
            else:
                cpf_supervisor = None
            
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
            import traceback
            print(traceback.format_exc())  
            return f"Erro: {str(e)}", 500
    
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)
    
    print(f"   📄 Mostrando formulário de edição")
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)

@app.route('/funcionario/delete/<string:pk>', methods=['GET', 'POST'])
def delete(pk):
    if request.method == 'POST':
        try:
            sucesso = funcionario_dao.delete('cpf', pk) 
            
            if sucesso:
                return redirect(url_for('index'))
            else:
                return "Erro ao excluir funcionário", 500
                
        except Exception as e:
            return f"Erro: {str(e)}", 500
    
    funcionario = funcionario_dao.read('cpf', pk)
    
    if not funcionario:
        return "Funcionário não encontrado", 404
        
    return render_template('delete.html', funcionario=funcionario, datetime=datetime)