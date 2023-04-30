from flask import render_template, request, redirect, make_response
import json

class Admin:
    def __init__(self, app, handler):
        self.app = app
        self.handler = handler
    
    def check_admin(self, key):
        user = self.handler.user.get(key)
        if user != None:
            if user['permission-level'] > 0: return True
            else: return False
    
    def admin(self):
        @self.app.route('/admin')
        def admin():
            key = request.cookies.get('key')
            if self.check_admin(key):
                return redirect('/admin/dashboard')
            else:
                return render_template("404.html")

    def dashboard(self):
        @self.app.route('/admin/dashboard')
        def admin_dash():
            key = request.cookies.get('key')
            if self.check_admin(key):
                return render_template('admin/dashboard.html', site='dashboard', user=self.handler.user.get(request.cookies.get('key')))
            else:
                return render_template("404.html")
            
        @self.app.route('/admin/dashboard/migrate')
        def admin_dash_migrate():
            key = request.cookies.get('key')
            if self.check_admin(key):
                self.handler.migrate()

                return redirect('/admin/dashboard')
            else:
                return render_template("404.html")

            
    def users(self):
        @self.app.route('/admin/users')
        def admin_users():
            key = request.cookies.get('key')
            if self.check_admin(key):
                return render_template('admin/users.html', users=self.handler.db.data['users'], site='users', user=self.handler.user.get(request.cookies.get('key')))
            else:
                return render_template("404.html")
            
        @self.app.route('/admin/users/<e_username>')
        def admin_user(e_username):
            key = request.cookies.get('key')
            if self.check_admin(key):
                e_user = self.handler.user.get_name(e_username)
                if e_user != None:
                    return render_template('admin/user.html', e_user=e_user, site='users', user=self.handler.user.get(request.cookies.get('key')))
                else:
                    return redirect('/admin/users')
            else:
                return render_template("404.html")
        
        @self.app.route('/admin/users/<e_username>/update', methods=['POST'])
        def admin_user_update(e_username):
            key = request.cookies.get('key')
            if self.check_admin(key):
                e_user = self.handler.user.get_name(e_username)
                if e_user != None:
                    for k in self.handler.user.default_user:
                        if isinstance(self.handler.user.default_user[k], int):
                            e_user[k] = int(request.form.get(k))
                        else:
                            e_user[k] = request.form.get(k)
                    self.handler.db.save()

                    return redirect('/admin/users/' + e_user['name'])
                else:
                    return redirect('/admin/users')
            else:
                return render_template("404.html")
        
        @self.app.route('/admin/users/<e_username>/remove')
        def admin_user_remove(e_username):
            key = request.cookies.get('key')
            if self.check_admin(key):
                e_user = self.handler.user.get_name(e_username)
                self.handler.user.remove(e_user['key'])

                return redirect('/admin/users')
            else:
                return render_template("404.html")
    
    def raw(self):
        @self.app.route('/admin/raw')
        def admin_raw():
            key = request.cookies.get('key')
            if self.check_admin(key):
                db_text = json.dumps(self.handler.db.data, indent=4)
                return render_template('admin/raw.html', db_text=db_text, rows=len(db_text.splitlines())+2, site='raw', user=self.handler.user.get(request.cookies.get('key')))

            else:
                return render_template("404.html")
            

    def run(self):
        self.admin()
        self.dashboard()
        self.users()
        self.raw()

