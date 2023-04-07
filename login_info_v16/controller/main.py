import os
import odoo
from odoo import http, tools, _
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.exceptions import UserError
from odoo.http import request
from datetime import date, datetime, time
import base64


class ImageController(Home):



    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False

        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # so it is correct if overloaded with auth="public"
        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        import cv2
        import base64
        cascPath = os.path.dirname(
            cv2.__file__) + "/data/haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(cascPath)
        if request.httprequest.method == 'POST':
            video = cv2.VideoCapture(0)
            while True:
                print('hloooo')
                ret, frames = video.read()
                print('hi')
                gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
                print('hi1')
                faces = faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE)
                print('jjjjjjjjjjj')
                for (x, y, w, h) in faces:
                    cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.imshow('Video', frames)
                    print('pppppppppp')
                k = cv2.waitKey(1)
                if k % 256 == 27:
                    break
                elif k % 256 == 13:
                    img_counter = 0
                    # img_name = f'opencv_frame_{img_counter}'
                    image=cv2.imwrite('/home/cybrosys/Desktop/img_name.jpg', frames)
                    with open("/home/cybrosys/Desktop/img_name.jpg", "rb") as img_file:
                        b64_string = base64.b64encode(img_file.read())
                    request.env['user.log'].sudo().create({'user':request.env.user.id, 'image':b64_string, 'date':datetime.now()})
                    video.release()
                    cv2.destroyAllWindows()
                    break

            try:
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
