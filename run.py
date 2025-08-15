# run.py

from src import create_app

# Cria a aplicação Flask usando a nossa "fábrica"
app = create_app()

if __name__ == '__main__':
    # O modo debug reinicia o servidor automaticamente a cada alteração no código.
    # Nunca use debug=True em produção!
    app.run(debug=True)