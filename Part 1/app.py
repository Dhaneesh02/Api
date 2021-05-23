from flask import Flask,request
import sqlite3
from datetime import date,datetime
from flask_restplus import Api, Resource, fields
from werkzeug import Authorization
from werkzeug.contrib.fixers import ProxyFix
from functools import wraps

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
authorizations = {
    'apikey':{
        'type':'apiKey',
        'in' : 'header',
        'name': 'X-API-KEY'
    }
}
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
    authorizations=authorizations
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by': fields.String(required=True,description='The last date to complete task'),
    'cur_status': fields.String(required=True,default='Not Started',description='The current status of the task')
})



def connect_db():
    return sqlite3.connect('todo.db')


class TodoDAO(object):

    def get(self, id):
        db=connect_db()
        query="Select * from todo where id='{}'".format(id)
        try:
            cur = db.execute(query)
            todo=[dict( id=row[0],task=row[1],due_by=row[2],cur_status=row[3]) for row in cur.fetchall()]
            db.close()
            if todo==[]:
                api.abort(404, "Todo {} doesn't exist".format(id))    
            return todo,200
        except:
            api.abort(404, "Unexpected error")
        

    def create(self, data):
        db=connect_db()
        query="INSERT INTO todo(task,due_by,cur_status) VALUES ('"+data['task']+"','"+data['due_by']+"','"+data['cur_status']+"')"
        #query='INSERT INTO TODO(task,due_by,cur_status) VALUES (?,?,?)',(data['task'],data['due_by'],data['cur_status'])
        try:
            db.execute(query)
            db.commit()
            db.close() 
            msg='todo created for task '+data['task']
            return {'message':msg},201
        except:
            api.abort(404, "Unexpected error")

    def update(self, id, data):
        todo=self.get(id)
        db=connect_db()
        query='UPDATE todo SET task="'+data['task']+'",due_by="'+data['due_by']+'",cur_status="'+data['cur_status']+'" where id="'+str(id)+'"'
        try:
            db.execute(query)
            db.commit()
            db.close()
            todo=self.get(id)
            return(todo)
        except:
            return {"Failure":"Error updating the database"}, 404

    def delete(self, id):
        self.get(id)
        db=connect_db()
        query='DELETE FROM todo where id={}'.format(id)
        try:
            db.execute(query)
            db.commit()
            db.close()
            return  {"Todo deleted successfully"},200
        except:
            api.abort(404, "Todo {} doesn't exist".format(id))

    def update_Status(self,id,new):
        db=connect_db()
        query="UPDATE todo SET cur_status='"+new+"' WHERE ID='"+str(id)+"'"
        try:
            print("hi")
            db.execute(query)
            print("hi3")
            db.commit()
            print("h2i")
            db.close()
            return self.get(id)
        except:
            api.abort(404, "Todo {} doesn't exist".format(id))
    
    def get_Finished(self):
        db=connect_db()
        query="SELECT * FROM todo where cur_status='Finished'"
        try:
            cur=db.execute(query)
            todos = [dict( id=row[0],task=row[1],due_by=row[2],cur_status=row[3]) for row in cur.fetchall()]
            db.commit()
            db.close()
            if todos is None: 
                api.abort(404, "Todo with finished status not found")    
            return todos,200
        except:
            api.abort(404, "Unexpected error")
    
    def get_Overdue(self):
        today = datetime.today()
        db=connect_db()
        print(today)
        query="SELECT * FROM todo"
        try:
            cur=db.execute(query)
            todos = [dict( id=row[0],task=row[1],due_by=row[2],cur_status=row[3]) for row in cur.fetchall()]
            over_due=[]
            for i in todos:
                if datetime.strptime(i['due_by'],'%Y-%m-%d') < today and i['cur_status'] != "Finished":
                    over_due.append(i)
            print(over_due,todos)
            db.commit()
            db.close()
            if over_due is None: 
                api.abort(404, "Todo with overdue status not found")    
            return over_due,200
        except:
            api.abort(404, "Unexpected error")
        
    def get_Due(self,date):
        db=connect_db()
        query="SELECT * FROM todo"
        try:
            cur=db.execute(query)
            todos = [dict( id=row[0],task=row[1],due_by=row[2],cur_status=row[3]) for row in cur.fetchall()]
            due=[]
            for i in todos:
                if datetime.strptime(i['due_by'],'%Y-%m-%d') == date and i['cur_status'] != "Finished":
                    due.append(i)
            db.commit()
            db.close()
            if due is None: 
                api.abort(404, "Todo with due status not found")    
            return due,200
        except:
            api.abort(404, "Unexpected error")
    
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message':'The Token is Required'},401
        if token != "dhaneesh":
            return {'message': 'The Token provided is not correct'},401
        return f(*args,**kwargs)
    return decorated

DAO = TodoDAO()
#DAO.create({'task': 'Build an API'})
#DAO.create({'task': '?????'})
#DAO.create({'task': 'profit!'})


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        db=connect_db()
        query="SELECT * FROM todo"
        cur=db.execute(query)
        todos = [dict( id=row[0],task=row[1],due_by=row[2],cur_status=row[3]) for row in cur.fetchall()]   
        db.close() 
        '''List all tasks'''
        return todos

    @ns.doc('create_todo',security='apikey')
    @token_required
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo',security='apikey')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.doc(security='apikey')
    @token_required
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/start/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class TodoStart(Resource):
    @ns.doc('start_todo',security='apikey')
    @token_required
    @ns.response(201, 'Todo Started')
    def get(self, id):
        '''Start a task given its identifier'''
        return DAO.update_Status(id,'In Progress'), 201
    
@ns.route('/finish/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class TodoFinish(Resource):
    @ns.doc('finish_todo',security='apikey')
    @token_required
    @ns.response(201, 'Todo Completed')
    def get(self, id):
        '''Finish a task given its identifier'''
        return DAO.update_Status(id,'Finished'), 201

@ns.route('/overdue')
@ns.response(404, 'No Overdue Tasks')
class TodoOverdue(Resource):
    @ns.doc('overdues')
    @ns.response(201, 'Overdue Todos Displayed')
    def get(self):
        '''Overdue tasks displayed'''
        return DAO.get_Overdue(), 201

@ns.route('/finished')
@ns.response(404, 'No Finished Tasks')
class TodoOverdue(Resource):
    @ns.doc('finished')
    @ns.response(201, 'Finished Todos Displayed')
    def get(self):
        '''Finished tasks displayed'''
        return DAO.get_Finished(), 201

@ns.route('/due')
@ns.response(404, 'No Todo due on this date found')
@ns.param('due_date', 'The task due date specified')
class TodoDue(Resource):
    @ns.doc('due')
    @ns.response(201, 'Todos due on the date is Displayed')
    def get(self):
        '''Finish a task given its identifier'''
        date=request.args['due_date']
        return DAO.get_Due(date), 201


if __name__ == '__main__':
    app.run(debug=True)