import werkzeug
from flask import request, url_for
from flask_jwt_extended import current_user, jwt_required
from flask_restplus import Resource, fields, abort, Namespace
from flask_restplus.reqparse import RequestParser

from ngsapp.common import phone_number
from ngsapp.common.schema import KYCSchema
from ngsapp.ext import pagination, db
from ngsapp.models import Kyc
from ngsapp.resources.users import user_schema
from ngsapp.utils import delete_file, file_upload, roles_required

parser = RequestParser(bundle_errors=True, trim=True)

parser.add_argument('business_name', required=True, location='json', type=str)
parser.add_argument('ident', required=True, location='json', type=str)
parser.add_argument('ident_name', required=True, location='json', type=str)
parser.add_argument('about_business', required=True, location='json', type=str)
parser.add_argument('phone_number', required=True, location='json', type=phone_number)
parser.add_argument('country', required=True, location='json', type=str)

ns_kyc = Namespace('kyc', 'Know your customer')
schema = KYCSchema()

mschema = ns_kyc.model('KYC', {
    'user': fields.Nested(user_schema),
    'business_name': fields.String(),
    'ident': fields.String(),
    'ident_name': fields.String(),
    'about_business': fields.String(),
    'phone_number': fields.String(),
    'country': fields.String(),
    'file': fields.String(),
    'status': fields.String(),
    'created': fields.DateTime(),
})


class KYCResourceList(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER']), jwt_required]

    def get(self):
        return pagination.paginate(Kyc, schema, True)


class KYCResource(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER']), jwt_required]

    @ns_kyc.marshal_with(mschema)
    def get(self, pk):
        obj = Kyc.query.get_or_404(pk)
        return obj

    def put(self, pk):
        put_parser = RequestParser(trim=True, bundle_errors=True)
        put_parser.add_argument('status', required=True, location='json', type=str,
                                choices=['Approved', 'Pending', 'Disapproved', 'Suspended', 'Processing'])
        args = put_parser.parse_args(strict=True)
        kyc = Kyc.query.get_or_404(pk)
        kyc.status = args.status
        return kyc.save(**args)

    def delete(self, pk):
        kyc = Kyc.query.get_or_404(pk)
        return kyc.delete(), 202


class ClientKYCResource(Resource):
    method_decorators = [roles_required(['CLIENT']), jwt_required]

    @ns_kyc.marshal_with(mschema)
    def get(self):
        return current_user.kyc_doc if current_user.kyc_doc else abort(404)

    def post(self):
        args = parser.parse_args(strict=True)
        if not current_user.kyc_doc:
            kyc = Kyc(**args)
            kyc.user_id = current_user.id
            return kyc.save(**args)
        return {'message': 'Resource already exist'}, 409

    def put(self):
        if current_user.kyc_doc:
            if current_user.kyc_doc.status != 'Pending':
                return {'message': 'You cant update kyc when not in pending state'}, 400
            args = parser.parse_args(strict=True)
            kyc = schema.load(data=request.json, instance=current_user.kyc_doc, session=db.session, unknown='exclude')
            return kyc.save(**args), 200
        else:
            return abort(404)

    def delete(self):
        doc = current_user.kyc_doc
        if doc:
            if doc.status != 'Pending':
                return {'message': 'You cant update kyc when not in pending state'}, 400
            delete_file(doc.file)
            return doc.delete(), 202
        return abort(404)


class KycUploadResource(Resource):
    method_decorators = [roles_required(['CLIENT']), jwt_required]
    file_parser = RequestParser(bundle_errors=True)

    # @ns_kyc.marshal_with(mschema)
    def post(self):
        doc = current_user.kyc_doc.status if current_user.kyc_doc else abort(404)
        if doc != 'Pending':
            return {'message': 'You cant update kyc when not in pending state'}, 400
        KycUploadResource.file_parser.add_argument('file', required=True, location='files',
                                                   type=werkzeug.datastructures.FileStorage)
        args = KycUploadResource.file_parser.parse_args(strict=True)
        kyc = current_user.kyc_doc
        if kyc.file:
            delete_file(kyc.file)
        file = file_upload(args.file)
        if file.get('error'):
            return file, 400
        file.get('upload').save(file.get('full_path'))
        args.update({'file': url_for('api.protected_dir', filename=file.get('filename'), _external=True)})
        kyc.file = file.get('filename')
        return kyc.save(**args), 200


ns_kyc.add_resource(KYCResourceList, '/', endpoint='kycs')
ns_kyc.add_resource(KYCResource, '/<int:pk>', endpoint='kyc')
ns_kyc.add_resource(ClientKYCResource, '/client', endpoint='client_kyc')
ns_kyc.add_resource(KycUploadResource, '/client/file', endpoint='client_kyc_file')
