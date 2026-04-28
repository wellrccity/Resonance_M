# Import all modules to initialize them
import src.pi_loader as pi_loader
import src.word_loader as word_loader
import src.generators as generators
import src.order as order
import src.analyzers as analyzers
import src.engines as engines
import src.workers as workers
import src.routes as routes

if __name__=='__main__':
    routes.app.run(host='127.0.0.1',port=5000,debug=False,threaded=True)
