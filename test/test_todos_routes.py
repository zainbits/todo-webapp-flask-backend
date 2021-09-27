import json
from test import BaseTestUser, BaseTestAdmin

from project import db
from project.todo.models import Todo


class TestTodoUser(BaseTestUser):

    def test_create_todo(self):
        response = self.client.post(
            "/todo",
            data=json.dumps
            (dict(text="test todo data 1234124")),
            headers={"Authorization": f"Bearer {self.token}"},
            content_type="application/json")
        assert response.status_code == 200
        todo = Todo.query.\
            filter_by(text="test todo data 1234124").\
            first()
        db.session.delete(todo)
        db.session.commit()

    def test_get_allusers_todos(self):
        response = self.client.get("/admin/todo/allusers",
                                   headers={"Authorization": f"Bearer {self.token}"})
        todos = json.loads(response.data)
        assert response.status_code == 403

    def test_get_all_todos(self):
        todo_new = Todo(text="test todo data 1234124",
                        user_id=5)
        db.session.add(todo_new)
        db.session.commit()

        response = self.client.get("/todo",
                                   headers={"Authorization": f"Bearer {self.token}"})
        todo = json.loads(response.data)

        db.session.delete(todo_new)
        db.session.commit()

        assert response.status_code == 200 and len(todo) > 0

    def test_update_a_todo(self):
        todo_new = Todo(id=123890,
                        text="test todo data 1234124",
                        user_id=5)
        db.session.add(todo_new)
        db.session.commit()
        response = self.client.put("/todo/123890",
        headers={"Authorization": f"Bearer {self.token}"},
        data=json.dumps(dict(
            complete=True,
        )), content_type="application/json")
        db.session.delete(todo_new)
        db.session.commit()
        assert response.status_code == 204



    def test_delete_todo(self):
        todo_new = Todo(id=123890,
                        text="test todo data 1234124",
                        user_id=5)
        db.session.add(todo_new)
        db.session.commit()
        response = self.client.delete("/todo/123890",
        headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 200
        try:
            db.session.delete(todo_new)
            db.session.commit()
        except:
            pass

    def test_delete_any_todo(self):
        todo_new = Todo(id=123890,
                        text="test todo data 1234124",
                        user_id=1)
        db.session.add(todo_new)
        db.session.commit()
        response = self.client.delete("admin/todo/123890",
        headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 403
        try:
            db.session.delete(todo_new)
            db.session.commit()
        except:
            print("user cannot delete any other users todo")

class TestTodoAdmin(BaseTestAdmin):

    def test_get_allusers_todos(self):
        response = self.client.get("/admin/todo/allusers",
                                   headers={"Authorization": f"Bearer {self.token}"})
        todos = json.loads(response.data)
        assert response.status_code == 200    


    def test_delete_any_todo(self):
        todo_new = Todo(id=123890,
                        text="test todo data 1234124",
                        user_id=1)
        db.session.add(todo_new)
        db.session.commit()
        response = self.client.delete("admin/todo/123890",
        headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 200
        try:
            db.session.delete(todo_new)
            db.session.commit()
        except:
            pass
