from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'e_segredo'


livros = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    generos = list(set([livro['genero'] for livro in livros]))
    return render_template('catalogo.html', livros=livros, generos=generos)

@app.route('/catalogo/<genero>')
def catalogo_por_genero(genero):
    livros_filtrados = [livro for livro in livros if livro['genero'] == genero]
    return render_template('catalogo.html', livros=livros_filtrados, generos=list(set([livro['genero'] for livro in livros])))

@app.route('/adicionar_livro', methods=['GET', 'POST'])
def adicionar_livro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']
        genero = request.form['genero']
        codigo = len(livros)
        devolver = "--/--/----"
        emprestado = False
        multa = 0
        livro = {
            'codigo': codigo,
            'titulo': titulo,
            'autor': autor,
            'ano': ano,
            'genero': genero,
            'emprestado': emprestado,
            'devolver': devolver,
            'multa': multa
        }
        livros.append(livro)
        flash(f'Livro {titulo} adicionado com sucesso!')
        return redirect('/catalogo')
    else:
        return render_template('adicionar_livro.html')

@app.route('/editar_livro/<int:codigo>', methods=['GET', 'POST'])
def editar_livro(codigo):
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']
        genero = request.form['genero']
        livros[codigo] = {
            'codigo': codigo,
            'titulo': titulo,
            'autor': autor,
            'ano': ano,
            'genero': genero,
            'emprestado': livros[codigo]['emprestado'],
            'devolver': livros[codigo]['devolver'],
            'multa': livros[codigo]['multa']
        }
        flash(f'Livro {titulo} atualizado!')
        return redirect('/catalogo')
    else:
        livro = livros[codigo]
        return render_template('editar_livro.html', livro=livro)

@app.route('/emprestar/<int:codigo>')
def emprestar(codigo):
    for livro in livros:
        if livro['codigo'] == codigo:
            livro['emprestado'] = True
            devolver = (datetime.now() + timedelta(days=-7)).strftime('%d/%m/%Y')
            livro['devolver'] = devolver
            livro['multa'] = 0
            flash(f'Livro {livro["titulo"]} emprestado com sucesso! Devolver até: {devolver}')
            return redirect('/catalogo')
    return redirect('/catalogo')

@app.route('/devolver/<int:codigo>')
def devolver(codigo):
    for livro in livros:
        if livro['codigo'] == codigo:
            data_devolucao = datetime.strptime(livro['devolver'], "%d/%m/%Y")
            dias_atraso = (datetime.now() - data_devolucao).days

            if dias_atraso > 0:
                multa = 10
                juros = (multa * (0.01 * dias_atraso))
                totalMulta = multa + juros
                livro['multa'] = totalMulta
                flash(f'Livro devolvido com {dias_atraso} dias de atraso. Multa: R${totalMulta}')
            else:
                livro['multa'] = 0
                flash(f'Livro devolvido dentro do prazo!')

            livro['emprestado'] = False
            livro['devolver'] = '--/--/----'
            return redirect('/catalogo')
    return redirect('/catalogo')

@app.route('/apagar_livro/<int:codigo>')
def apagar_livro(codigo):
    del livros[codigo]
    flash(f'Livro excluído!')
    return redirect('/catalogo')

if __name__ == '__main__':
    app.run(debug=True)